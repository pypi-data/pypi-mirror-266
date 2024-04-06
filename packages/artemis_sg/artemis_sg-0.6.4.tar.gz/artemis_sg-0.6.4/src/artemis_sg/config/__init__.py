import logging
import os

from flatten_dict import flatten, unflatten

import artemis_sg

namespace = "artemis_sg.config"

# Everyghing that can be configured is here.
CFG = {
    "asg": {
        "vendors": [
            {"code": "sample",
             "name": "Sample Vendor",
             "isbn_key": "ISBN-13",
             "failover_scraper": ""},
            {"code": "sample2",
             "name": "Another Vendor",
             "isbn_key": "ISBN",
             "failover_scraper": "AmznUkScraper"},
        ],
        "item": {
            "sort_order": [
                "TITLE",
                "SUBTITLE",
                "AUTHOR",
                "PUBLISHER",
                "PUB DATE",
                "PUBLISHERDATE",
                "FORMAT",
            ],
        },
        "spreadsheet": {
            "sheet_image": {
                "col_order": [
                    "ISBN",
                    "IMAGE",
                    "ORDER",
                ],
                "image_row_height": 105,
                "image_col_width": 18,
                "isbn_col_width": 13,
                "max_col_width": 50,
                "col_buffer": 1.23,
            },
            "mkthumbs": {
                "width": 130,
                "height": 130,
            },
        },
        "scraper": {
            "headless": False,
            "login_timeout": 90,
            "gjscraper": {
                "sentinel_publisher": "Abbeville",
            },
        },
        "data": {
            "file": {
                "scraped": os.path.join(artemis_sg.data_dir, "scraped_items.json"),
            },
            "dir": {
                "images": os.path.join(artemis_sg.data_dir, "downloaded_images"),
                "upload_source": os.path.join(artemis_sg.data_dir, "downloaded_images"),
            },
        },
        "slide_generator": {
            "title_default": "New Arrivals",
            "line_spacing": 1,
            "text_width": 80,
            "max_fontsize": 18,
            "slide_max_batch": 25,
            "slide_ppi": 96,
            "slide_w": 10.0,
            "slide_h": 5.625,
            "gutter": 0.375,
            "text_box_resize_img_threshold": 2,
            "logo_h": 1,
            "logo_w": 1,
            "addl_img_h": 1.5,
            "addl_img_w": 3,
            "logo_url": "https://images.squarespace-cdn.com/content/v1/6110970ca45ca157a1e98b76/e4ea0607-01c0-40e0-a7c0-b56563b67bef/artemis.png?format=1500w",
            "blacklist_keys": (
                "IMAGE",
                "ON HAND",
                "ORDER",
                "ORDER QTY",
                "GJB SUGGESTED",
                "DATE RECEIVED",
                "SUBJECT",
                "QTYINSTOCK",
                "QTY",
                "SALESPRICE",
                "AVAILABLE START DATE",
                "CATEGORY",
                "LINK",
                ),
            "gj_binding_map": {
                "P": "Paperback",
                "H": "Hardcover",
                "C": "Hardcover",
                "C NDJ": "Cloth, no dust jacket",
                "CD": "CD",
            },
            "gj_type_map": {
                "R": "Remainder",
                "H": "Return"
            },
            "bg_color": "black",
            "text_color": "white",
            "tiny_isbn_x_inset": 1.0,
            "tiny_isbn_fontsize": 6,
            "text_box_max_lines": 36,
            "text_box_resized_max_lines": 28,
            "text_map": {
                "AUTHOR": "by {t}",
                "PUB LIST": "List Price: {t}",
                "LISTPRICE": "List Price: {t}",
                "USD COST": "USD Cost: ${t}",
                "RRP": "List price: £{t}",
                "BARGAIN": "Bargain: £{t}",
                "NET COST": "Your Net Price: {t}",
                "YOUR NET PRICE": "Your Net Price: {t}",
                "PUB DATE": "Pub Date: {t}",
                "PUBLISHERDATE": "Pub Date: {t}",
                "BINDING": "Format: {t}",
                "FORMAT": "Format: {t}",
                "TYPE": "Type: {t}",
                "PAGES": "Pages: {t} pp.",
                "SIZE": "Size: {t}",
                "ITEM#": "Item #: {t}",
                "TBCODE": "Item #: {t}",
            },
        },
        "test": {
            "sheet": {"id": "GOOGLE_SHEET_ID_HERE", "tab": "GOOGLE_SHEET_TAB_HERE"}
        },
    },
    "google": {
        "cloud": {
            "new_threshold_secs": 3600,
            "bucket": "my_bucket",
            "bucket_prefix": "my_bucket_prefix",
            "key_file": os.path.join(
                artemis_sg.data_dir, "google_cloud_service_key.json"
            ),
        },
        "docs": {
            "api_creds_file": os.path.join(artemis_sg.data_dir, "credentials.json"),
            "api_creds_token": os.path.join(
                artemis_sg.data_dir, "app_creds_token.json"
            ),
        },
    },
}

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

conf_file = "config.toml"

conf_path = os.path.join(artemis_sg.conf_dir, conf_file)

try:
    with open(conf_path, mode="rb") as fp:
        f_config = tomllib.load(fp)
except FileNotFoundError:
    import tomli_w

    logging.warning(f"{namespace}: Config file not found at {conf_path}.")
    logging.warning(f"{namespace}: Creating new config file at {conf_path}.")
    logging.warning(
        f"{namespace}: IMPORTANT: Edit file to set proper values for google_cloud."
    )

    d = os.path.dirname(conf_path)
    if not os.path.exists(d):
        os.makedirs(d)
    with open(conf_path, mode="wb") as fp:
        tomli_w.dump(CFG, fp)
    with open(conf_path, mode="rb") as fp:
        f_config = tomllib.load(fp)

# Update CFG with contents of f_config
flat_cfg = flatten(CFG)
flat_f_config = flatten(f_config)
flat_merged = flat_cfg | flat_f_config
CFG = unflatten(flat_merged)

# Create all defined data_dir subdirectories
for key in CFG["asg"]["data"]["dir"]:
    d = CFG["asg"]["data"]["dir"][key]
    if not os.path.exists(d):
        logging.warning(f"{namespace}: Creating new directory at {d}.")
        os.makedirs(d)

# Create all defined data_dir files
for key in CFG["asg"]["data"]["file"]:
    f = CFG["asg"]["data"]["file"][key]
    if not os.path.exists(f):
        d = os.path.dirname(f)
        if not os.path.exists(d):
            logging.warning(f"{namespace}: Creating new directory at {d}.")
            os.makedirs(d)
        logging.warning(f"{namespace}: Creating new file at {f}.")
        _root, ext = os.path.splitext(f)
        with open(f, "w") as fp:
            # Seed JSON files with valid empty JSON.
            if ext.lower() == ".json":
                fp.write("{ }")
            pass
