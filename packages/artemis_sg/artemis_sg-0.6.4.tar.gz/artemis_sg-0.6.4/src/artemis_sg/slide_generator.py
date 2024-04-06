import datetime
import logging
import math
import os
import textwrap

from PIL import Image, ImageColor, ImageDraw, ImageFont
from rich.console import Console
from rich.text import Text

import artemis_sg
from artemis_sg import spreadsheet
from artemis_sg.config import CFG

console = Console()


class SlideGenerator:
    # constants
    EMU_INCH = 914400

    # methods
    def __init__(self, slides, gcloud, vendor):
        self.slides = slides
        self.gcloud = gcloud
        self.vendor = vendor
        self.slides_api_call_count = 0

    ###########################################################################
    def color_to_rgbcolor(self, color):
        red, green, blue = ImageColor.getrgb(color)
        return {
                "red": red/255.0,
                "green": green/255.0,
                "blue": blue/255.0
                }

    def gj_binding_map(self, code):
        code = code.upper()
        return CFG["asg"]["slide_generator"]["gj_binding_map"].get(code, code)

    def gj_type_map(self, code):
        code = code.upper()
        return CFG["asg"]["slide_generator"]["gj_type_map"].get(code, code)

    def get_req_update_artemis_slide(
        self, deck_id, book_slide_id, item, text_bucket_path, g_reqs
    ):
        namespace = (
            f"{type(self).__name__}.{self.get_req_update_artemis_slide.__name__}"
        )

        bg_color = CFG["asg"]["slide_generator"]["bg_color"]
        slide_w = CFG["asg"]["slide_generator"]["slide_w"]
        slide_h = CFG["asg"]["slide_generator"]["slide_h"]
        gutter = CFG["asg"]["slide_generator"]["gutter"]
        addl_img_w = CFG["asg"]["slide_generator"]["addl_img_w"]
        addl_img_h = CFG["asg"]["slide_generator"]["addl_img_h"]
        image_count = len(item.image_urls)
        main_dim = self.get_main_image_size(image_count)

        logging.info(f"{namespace}: background to {bg_color}")
        g_reqs += self.get_req_slide_bg_color(
                book_slide_id,
                self.color_to_rgbcolor(bg_color))

        logging.info(f"{namespace}: cover image on book slide")
        cover_url = item.image_urls.pop()
        g_reqs += self.get_req_create_image(
            book_slide_id,
            cover_url,
            main_dim,
            (gutter, gutter),
        )

        for i, url in enumerate(item.image_urls):
            if i > CFG["asg"]["slide_generator"]["text_box_resize_img_threshold"]:
                continue

            logging.info(f"{namespace}: {i + 2!s} image on book slide")
            g_reqs += self.get_req_create_image(
                book_slide_id,
                url,
                (addl_img_w, addl_img_h),
                (
                    (gutter + ((addl_img_w + gutter) * i)),
                    (slide_h - gutter - addl_img_h),
                ),
            )

        logging.info(f"{namespace}: Create text")
        text_box_dim, max_lines = self.get_text_box_size_lines(image_count)
        big_text = self.create_slide_text(item, max_lines)

        logging.info(f"{namespace}: Create text image")
        text_filepath = self.create_text_image_file(
            item.isbn, text_bucket_path, big_text, text_box_dim
        )

        logging.info(f"{namespace}: Upload text image to GC storage")
        cdr, car_file = os.path.split(text_filepath)
        cdr, car_prefix = os.path.split(cdr)
        blob_name = car_prefix + "/" + car_file
        self.gcloud.upload_cloud_blob(text_filepath, blob_name)
        logging.debug(f"{namespace}: Deleting local text image")
        os.remove(text_filepath)
        logging.info(f"{namespace}: Create URL for text image")
        url = self.gcloud.generate_cloud_signed_url(blob_name)
        logging.info(f"{namespace}: text image to slide")
        g_reqs += self.get_req_create_image(
            book_slide_id, url, text_box_dim, (slide_w / 2, gutter)
        )

        logging.info(f"{namespace}: ISBN text on book slide")
        text_box_w = slide_w
        text_box_h = gutter
        text_fields = self.create_text_fields_via_batch_update(
            deck_id,
            self.get_req_create_text_box(
                book_slide_id,
                (slide_w - CFG["asg"]["slide_generator"]["tiny_isbn_x_inset"],
                 slide_h - gutter),
                (text_box_w, text_box_h),
            ),
        )
        text_field_id = text_fields[0]
        text_d = {text_field_id: item.isbn}
        g_reqs += self.get_req_insert_text(text_d)
        g_reqs += self.get_req_text_field_fontsize(
                text_field_id,
                CFG["asg"]["slide_generator"]["tiny_isbn_fontsize"])
        g_reqs += self.get_req_text_field_color(
                text_field_id,
                self.color_to_rgbcolor(CFG["asg"]["slide_generator"]["text_color"]))

        logging.info(f"{namespace}: logo image on book slide")
        g_reqs += self.get_req_create_logo(book_slide_id)

        return g_reqs

    def create_text_fields_via_batch_update(self, deck_id, reqs):
        text_object_id_list = []
        rsp = self.slide_batch_update_get_replies(deck_id, reqs)
        for obj in rsp:
            text_object_id_list.append(obj["createShape"]["objectId"])
        return text_object_id_list

    def create_book_slides_via_batch_update(self, deck_id, book_list):
        namespace = (
            f"{type(self).__name__}.{self.create_book_slides_via_batch_update.__name__}"
        )

        logging.info(f"{namespace}: Create slides for books")
        book_slide_id_list = []
        reqs = []
        for _i in range(len(book_list)):
            reqs += [
                {"createSlide": {"slideLayoutReference": {"predefinedLayout": "BLANK"}}}
            ]
        rsp = self.slide_batch_update_get_replies(deck_id, reqs)
        for i in rsp:
            book_slide_id_list.append(i["createSlide"]["objectId"])
        return book_slide_id_list

    def slide_batch_update(self, deck_id, reqs):
        try:
            res = (
            self.slides.presentations()
            .batchUpdate(body={"requests": reqs}, presentationId=deck_id)
            .execute()
            )
        except Exception as e:
            logging.error(f"Failed to update slide batch: Errror: {e}")
            res = None

        return res

    def slide_batch_update_get_replies(self, deck_id, reqs):
        return (
            self.slides.presentations()
            .batchUpdate(body={"requests": reqs}, presentationId=deck_id)
            .execute()
            .get("replies")
        )

    def get_req_create_image(self, slide_id, url, size, translate):
        w, h = size
        translate_x, translate_y = translate
        reqs = [
            {
                "createImage": {
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": {
                            "width": {
                                "magnitude": self.EMU_INCH * w,
                                "unit": "EMU",
                            },
                            "height": {
                                "magnitude": self.EMU_INCH * h,
                                "unit": "EMU",
                            },
                        },
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": self.EMU_INCH * translate_x,
                            "translateY": self.EMU_INCH * translate_y,
                            "unit": "EMU",
                        },
                    },
                    "url": url,
                },
            }
        ]
        return reqs

    def get_req_create_logo(self, slide_id):
        # Place logo in upper right corner of slide
        # TODO: (#163) move this to CFG
        translate_x = (
                CFG["asg"]["slide_generator"]["slide_w"] -
                CFG["asg"]["slide_generator"]["logo_w"])
        translate_y = 0
        return self.get_req_create_image(
            slide_id,
            CFG["asg"]["slide_generator"]["logo_url"],
            (
                CFG["asg"]["slide_generator"]["logo_w"],
                CFG["asg"]["slide_generator"]["logo_h"]
            ),
            (translate_x, translate_y),
        )

    def get_req_slide_bg_color(self, slide_id, rgb_d):
        reqs = [
            {
                "updatePageProperties": {
                    "objectId": slide_id,
                    "fields": "pageBackgroundFill",
                    "pageProperties": {
                        "pageBackgroundFill": {
                            "solidFill": {
                                "color": {
                                    "rgbColor": rgb_d,
                                }
                            }
                        }
                    },
                },
            },
        ]
        return reqs

    def get_req_text_field_color(self, field_id, rgb_d):
        reqs = [
            {
                "updateTextStyle": {
                    "objectId": field_id,
                    "textRange": {"type": "ALL"},
                    "style": {
                        "foregroundColor": {
                            "opaqueColor": {
                                "rgbColor": rgb_d,
                            }
                        }
                    },
                    "fields": "foregroundColor",
                }
            }
        ]
        return reqs

    def get_req_text_field_fontsize(self, field_id, pt_size):
        reqs = [
            {
                "updateTextStyle": {
                    "objectId": field_id,
                    "textRange": {"type": "ALL"},
                    "style": {
                        "fontSize": {
                            "magnitude": pt_size,
                            "unit": "PT",
                        }
                    },
                    "fields": "fontSize",
                }
            },
        ]
        return reqs

    def get_req_insert_text(self, text_dict):
        reqs = []
        for key in text_dict:
            reqs.append(
                {
                    "insertText": {
                        "objectId": key,
                        "text": text_dict[key],
                    },
                }
            )
        return reqs

    def get_req_create_text_box(self, slide_id, coord=(0, 0), field_size=(1, 1)):
        reqs = [
            {
                "createShape": {
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": {
                            "width": {
                                "magnitude": self.EMU_INCH * field_size[0],
                                "unit": "EMU",
                            },
                            "height": {
                                "magnitude": self.EMU_INCH * field_size[1],
                                "unit": "EMU",
                            },
                        },
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": self.EMU_INCH * coord[0],
                            "translateY": self.EMU_INCH * coord[1],
                            "unit": "EMU",
                        },
                    },
                    "shapeType": "TEXT_BOX",
                },
            }
        ]
        return reqs

    def get_slide_text_key_map(self, key, item):
        t = str(item.data[key])
        # hacky exceptions
        if key == "BINDING":
            t = self.gj_binding_map(t)
        if key == "TYPE":
            t = self.gj_type_map(t)
        try:
            fstr = CFG["asg"]["slide_generator"]["text_map"][key]
        except KeyError:
            fstr = "ISBN: {t}" if key == item.isbn_key else key.title() + ": {t}"
        return fstr.format(t = t)

    def create_slide_text(self, item, max_lines):
        namespace = f"{type(self).__name__}.{self.create_slide_text.__name__}"

        big_text = ""
        logging.debug(f"{namespace}: Item.data: {item.data}")
        for k in item.data:
            key = k.strip().upper()
            if key in CFG["asg"]["slide_generator"]["blacklist_keys"]:
                continue
            t = self.get_slide_text_key_map(key, item)
            line_count = big_text.count("\n")
            t = textwrap.fill(
                t,
                width=CFG["asg"]["slide_generator"]["text_width"],
                max_lines=max_lines - line_count
            )
            t = t + "\n\n"
            big_text += t
        return big_text

    def create_text_image_file(self, isbn, text_bucket_path, text, size):
        namespace = f"{type(self).__name__}.{self.create_text_image_file.__name__}"

        line_spacing = CFG["asg"]["slide_generator"]["line_spacing"]
        slide_ppi = CFG["asg"]["slide_generator"]["slide_ppi"]
        w, h = size
        image = Image.new(
            "RGB",
            (int(w * slide_ppi), int(h * slide_ppi)),
            ImageColor.getrgb(CFG["asg"]["slide_generator"]["bg_color"]),
        )

        fontsize = 1
        for typeface in (
            "arial.ttf",
            "LiberationSans-Regular.ttf",
            "DejaVuSans.ttf",
        ):
            try:
                font = ImageFont.truetype(typeface, fontsize)
                break
            except OSError:
                font = None
                continue
        if not font:
            logging.error(f"{namespace}: Cannot access typeface '{typeface}'")
            return None
        draw = ImageDraw.Draw(image)

        # dynamically size text to fit box
        while (
            draw.multiline_textbbox(
                xy=(0, 0), text=text, font=font, spacing=line_spacing
            )[2]
            < image.size[0]
            and draw.multiline_textbbox(
                xy=(0, 0), text=text, font=font, spacing=line_spacing
            )[3]
            < image.size[1]
            and fontsize < CFG["asg"]["slide_generator"]["max_fontsize"]
        ):
            fontsize += 1
            font = ImageFont.truetype(typeface, fontsize)

        fontsize -= 1
        logging.info(f"{namespace}: Font size is '{fontsize}'")
        font = ImageFont.truetype(typeface, fontsize)

        # center text
        _delme1, _delme2, t_w, t_h = draw.multiline_textbbox(
            xy=(0, 0), text=text, font=font, spacing=line_spacing
        )
        y_offset = math.floor((image.size[1] - t_h) / 2)

        draw.multiline_text(
            (0, y_offset), text, font=font, spacing=line_spacing
        )  # put the text on the image
        text_file = "%s_text.png" % isbn
        text_file = os.path.join(text_bucket_path, text_file)
        image.save(text_file)
        return text_file

    def set_image_blob_list(self, bucket_prefix):
        self.image_blob_list = self.gcloud.list_image_blob_names(bucket_prefix)

    def get_item_image_blob_list(self, item):
        # FIXME:  This should happen in Item object at time of instantiation.
        if not item.isbn and "TBCODE" in item.data:
            item.isbn = item.data["TBCODE"]
        image_list = [blob for blob in self.image_blob_list if str(item.isbn) in blob]
        return sorted(image_list)

    def get_cloud_urls(self, item):
        sl = self.get_item_image_blob_list(item)
        # generate URLs for item images on google cloud storage
        url_list = []
        for name in sl:
            url = self.gcloud.generate_cloud_signed_url(name)
            url_list.append(url)

        return url_list

    def get_text_bucket_prefix(self, bucket_prefix):
        # hack a text_bucket_prefix value
        text_bucket_prefix = bucket_prefix.replace("images", "text")
        if text_bucket_prefix == bucket_prefix:
            text_bucket_prefix = bucket_prefix + "_text"
        return text_bucket_prefix

    ####################################################################################
    def generate(self, items, bucket_prefix, deck_title=None):  # noqa: PLR0915
        namespace = f"{type(self).__name__}.{self.generate.__name__}"

        logging.info(f"{namespace}: Getting image blob list")
        self.set_image_blob_list(bucket_prefix)

        slide_max_batch = CFG["asg"]["slide_generator"]["slide_max_batch"]
        text_bucket_prefix = self.get_text_bucket_prefix(bucket_prefix)
        text_bucket_path = os.path.join(artemis_sg.data_dir, text_bucket_prefix)
        if not os.path.isdir(text_bucket_path):
            os.mkdir(text_bucket_path)

        logging.info(f"{namespace}: Create new slide deck")
        utc_dt = datetime.datetime.now(datetime.timezone.utc)
        local_time = utc_dt.astimezone().isoformat()
        title = f"{self.vendor.vendor_name} Artemis Slides {local_time}"
        data = {"title": title}
        rsp = self.slides.presentations().create(body=data).execute()
        self.slides_api_call_count += 1
        deck_id = rsp["presentationId"]

        title_slide = rsp["slides"][0]
        title_slide_id = title_slide["objectId"]
        title_id = title_slide["pageElements"][0]["objectId"]
        subtitle_id = title_slide["pageElements"][1]["objectId"]

        reqs = []
        logging.info(f"{namespace}: req Insert slide deck title+subtitle")
        subtitle = self.vendor.vendor_name
        if deck_title:
            subtitle = f"{subtitle}, {deck_title}"
        title_card_text = {
            title_id: "Artemis Book Sales Presents...",
            subtitle_id: subtitle,
        }
        reqs += self.get_req_insert_text(title_card_text)
        reqs += self.get_req_text_field_fontsize(title_id, 40)
        reqs += self.get_req_text_field_color(
                title_id,
                self.color_to_rgbcolor(CFG["asg"]["slide_generator"]["text_color"]))
        reqs += self.get_req_text_field_color(
                subtitle_id,
                self.color_to_rgbcolor(CFG["asg"]["slide_generator"]["text_color"]))
        reqs += self.get_req_slide_bg_color(
                title_slide_id,
                self.color_to_rgbcolor(CFG["asg"]["slide_generator"]["bg_color"]))
        reqs += self.get_req_create_logo(title_slide_id)

        # find images and delete books entries without images
        # using blob list as proxy for final urls to be generated later.
        for item in items:
            item.image_urls = self.get_item_image_blob_list(item)

        # update title slide
        self.slide_batch_update(deck_id, reqs)
        # clear reqs
        reqs = []
        # create book slides
        items_with_images = items.get_items_with_image_urls()
        book_slide_id_list = self.create_book_slides_via_batch_update(
            deck_id, items_with_images
        )

        e_books = list(zip(book_slide_id_list, items_with_images))
        batches = math.ceil(len(e_books) / slide_max_batch)
        upper_index = len(e_books)
        offset = 0
        for _b in range(batches):
            upper = offset + slide_max_batch
            if upper > upper_index:
                upper = upper_index
            for book_slide_id, book in e_books[offset:upper]:
                book.image_urls = self.get_cloud_urls(book)
                reqs = self.get_req_update_artemis_slide(
                    deck_id, book_slide_id, book, text_bucket_path, reqs
                )
            logging.info(f"{namespace}: Execute img/text update reqs")
            # pp.pprint(reqs)
            # exit()
            self.slide_batch_update(deck_id, reqs)
            reqs = []
            offset = offset + slide_max_batch

        logging.info(f"{namespace}: Slide deck completed")
        logging.info(f"{namespace}: API call counts")
        link = f"https://docs.google.com/presentation/d/{deck_id}"
        logging.info(f"{namespace}: Slide deck link: {link}")
        return link

    def get_main_image_size(self, image_count):
        w = (
                (CFG["asg"]["slide_generator"]["slide_w"] / 2)
                - (CFG["asg"]["slide_generator"]["gutter"] * 2)
            )
        h = (
                CFG["asg"]["slide_generator"]["slide_h"]
                - (CFG["asg"]["slide_generator"]["gutter"] * 2)
            )
        if image_count > 1:
            h = (
                    CFG["asg"]["slide_generator"]["slide_h"]
                    - (CFG["asg"]["slide_generator"]["gutter"] * 3)
                    - (CFG["asg"]["slide_generator"]["addl_img_h"])
                )
        return (w, h)

    def get_text_box_size_lines(self, image_count):
        w = (
                (CFG["asg"]["slide_generator"]["slide_w"] / 2)
                - (CFG["asg"]["slide_generator"]["gutter"] * 2)
            )
        h = (
                CFG["asg"]["slide_generator"]["slide_h"]
                - (CFG["asg"]["slide_generator"]["gutter"] * 2)
            )
        max_lines = CFG["asg"]["slide_generator"]["text_box_max_lines"]
        if (
                image_count
                > CFG["asg"]["slide_generator"]["text_box_resize_img_threshold"]
           ):
            h = (
                    CFG["asg"]["slide_generator"]["slide_h"]
                    - (CFG["asg"]["slide_generator"]["gutter"] * 2)
                    - (CFG["asg"]["slide_generator"]["addl_img_h"])
                )
            max_lines = CFG["asg"]["slide_generator"]["text_box_resized_max_lines"]
        return (w, h), max_lines

    ###########################################################################


def main(vendor_code, sheet_id, worksheet, scraped_items_db, title):
    # namespace = "slide_generator.main"
    from googleapiclient.discovery import build

    from artemis_sg.app_creds import app_creds
    from artemis_sg.gcloud import GCloud
    from artemis_sg.items import Items
    from artemis_sg.vendor import Vendor

    # vendor object
    vendr = Vendor(vendor_code)
    vendr.set_vendor_data()

    # Slides API object
    creds = app_creds()
    slides = build("slides", "v1", credentials=creds)

    # GCloud object
    bucket_name = CFG["google"]["cloud"]["bucket"]
    cloud_key_file = CFG["google"]["cloud"]["key_file"]
    gcloud = GCloud(cloud_key_file=cloud_key_file, bucket_name=bucket_name)

    sheet_data = spreadsheet.get_sheet_data(sheet_id, worksheet)

    sheet_keys = sheet_data.pop(0)
    items_obj = Items(sheet_keys, sheet_data, vendr.isbn_key)
    items_obj.load_scraped_data(scraped_items_db)

    sg = SlideGenerator(slides, gcloud, vendr)

    bucket_prefix = CFG["google"]["cloud"]["bucket_prefix"]
    slide_deck = sg.generate(items_obj, bucket_prefix, title)
    deck_text = Text(f"Slide deck: {slide_deck}")
    deck_text.stylize("green")
    console.print(deck_text)
