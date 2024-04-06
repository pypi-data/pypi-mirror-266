import contextlib
import json
import logging
import os
import string
import tempfile

from artemis_sg.item import Item


class Items:
    """
    Collection object for artemis_slide_generaor.Item objects.
    """

    # Constants
    ALPHA_LIST = tuple(string.ascii_uppercase)

    # methods
    def __init__(self, keys, value_list, isbn_key):
        """
        Instantiate Items object

        Arguments:
        keys -- list of strings to use as item keys
        value_list -- list of value lists, nested list positions correspond to keys
        isbn_key -- the key in keys that corresponds with ISBN (primary key)

        Returns:
        Items object
        """
        namespace = f"{type(self).__name__}.{self.__init__.__name__}"

        len_keys = len(keys)
        len_vals = len(value_list[0])
        if len_keys != len_vals:
            logging.error(
                f"{namespace}: Key count ({len_keys}) "
                f"does not match value count ({len_vals})."
            )
            logging.debug(f"keys: {keys}")
            logging.debug(f"first_row values: {value_list[0]}")
            raise IndexError

        self.isbn_key = isbn_key
        self.column_dict = dict(zip(keys, Items.ALPHA_LIST))

        self.items = []
        for row_num, entry in enumerate(value_list):
            i = Item(keys, entry, row_num, self.isbn_key)
            if any(i.data.values()):
                self.items.append(i)

    def get_items(self):
        return self.items

    def __iter__(self):
        return iter(self.items)

    def get_json_data_from_file(self, datafile):
        namespace = f"{type(self).__name__}.{self.get_json_data_from_file.__name__}"
        try:
            with open(datafile) as filepointer:
                data = json.load(filepointer)
            return data
        except FileNotFoundError:
            logging.error(f"{namespace}: Datafile '{datafile}' not found")
            return {}
        except json.decoder.JSONDecodeError:
            logging.error(
                f"{namespace}: Datafile '{datafile}' did not contain valid JSON"
            )
            return {}

    def load_scraped_data(self, datafile):
        data = self.get_json_data_from_file(datafile)
        self.set_scraped_data(data)

    def save_scraped_data(self, datafile):
        namespace = f"{type(self).__name__}.{self.save_scraped_data.__name__}"

        internal_data = self.get_scraped_data()
        external_data = self.get_json_data_from_file(datafile)
        external_data.update(internal_data)
        if external_data:
            content = json.dumps(external_data, indent=4)
            logging.debug(f"{namespace}: saving scraped data to {datafile}")
            self._atomic_write(content, datafile)

    def set_scraped_data(self, data):
        for isbn in data:
            item = self.find_item(isbn)
            if not item:
                continue
            try:
                item.data["DESCRIPTION"] = data[isbn]["DESCRIPTION"]
            except KeyError:
                item.data["DESCRIPTION"] = ""
            try:
                item.data["DIMENSION"] = data[isbn]["DIMENSION"]
            except KeyError:
                item.data["DIMENSION"] = ""
            item.image_urls = data[isbn]["image_urls"]

    def get_scraped_data(self):
        data = {}
        for item in self.items:
            if item.image_urls != []:
                data_elem = {}
                data_elem["isbn10"] = item.isbn10
                data_elem["image_urls"] = item.image_urls
                if "DESCRIPTION" in item.data:
                    data_elem["DESCRIPTION"] = item.data["DESCRIPTION"]
                if "DIMENSION" in item.data:
                    data_elem["DIMENSION"] = item.data["DIMENSION"]
                data[item.isbn] = data_elem

        return data

    def find_item(self, isbn):
        for item in self.items:
            if item.isbn == isbn:
                return item
        return None

    def get_items_with_image_urls(self):
        # WARNING: this looks a scraped urls to determine if the item has images.
        #   Images may be retrieved from GCloud storage.  So, there may be cases
        #   where this method of searching leads to false positives/negatives.
        items_with_images = []
        for item in self.items:
            if item.image_urls != []:
                items_with_images.append(item)
        return items_with_images


    def _atomic_write(self, file_contents, target_file_path, mode="w"):
        """Write to a temporary file and rename it to avoid file corruption.
        Attribution: @therightstuff, @deichrenner, @hrudham
        :param file_contents: contents to be written to file
        :param target_file_path: the file to be created or replaced
        :param mode: the file mode defaults to "w", only "w" and "a" are supported
        """
        # Use the same directory as the destination file so that moving it across
        # file systems does not pose a problem.
        try:
            # preserve file metadata if it already exists
            # if os.path.exists(target_file_path):
            #     shutil.copy2(source, target)
            with tempfile.NamedTemporaryFile(
                    mode=mode,
                    delete=False,
                    dir=os.path.dirname(target_file_path)) as temp_file:
                temp_file.write(file_contents)
                temp_file.flush()
                os.fsync(temp_file.fileno())

            os.replace(temp_file.name, target_file_path)
        finally:
            if os.path.exists(temp_file.name):
                with contextlib.suppress(IOError):
                    os.unlink(temp_file.name)
