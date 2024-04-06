# ruff: noqa: S101
from artemis_sg import vendor


class TestVendor:
    def test_create_vendor(self):
        """
        GIVEN Vendor with vendor code
        WHEN Vendor instance is created
        THEN the instances vendor_code attribute is set to the given code
        """
        vendr = vendor.Vendor("foo")

        assert vendr.vendor_code == "foo"

    def test_set_vendor_data_subset(self, monkeypatch):
        """
        GIVEN a vendor whose code is in the database
        WHEN the set_vendor_data method is called
        THEN the expected attributes are set even when keys are missing
        """
        data = [
            {
                "code": "sample",
                "name": "Super Sample Test Vendor",
                "isbn_key": "ISBN-13",
            }
        ]
        monkeypatch.setitem(vendor.CFG["asg"], "vendors", data)
        vendor_code = "sample"
        vendr = vendor.Vendor(vendor_code)
        vendr.set_vendor_data()

        assert vendr.vendor_code == vendor_code
        assert vendr.vendor_name == "Super Sample Test Vendor"
        assert vendr.isbn_key == "ISBN-13"

    def test_set_vendor_data_superset(self, monkeypatch):
        """
        GIVEN a vendor whose code is in the database
        WHEN the set_vendor_data method is called
        THEN the expected attributes are set even with surplus keys
        """
        data = [
            {
                "code": "sample",
                "name": "Super Sample Test Vendor",
                "isbn_key": "ISBN-13",
                "failover_scraper": "KoolScraper",
                "extra_key": "unused",
            }
        ]
        monkeypatch.setitem(vendor.CFG["asg"], "vendors", data)
        vendor_code = "sample"
        vendr = vendor.Vendor(vendor_code)
        vendr.set_vendor_data()

        assert vendr.vendor_code == vendor_code
        assert vendr.vendor_name == "Super Sample Test Vendor"
        assert vendr.isbn_key == "ISBN-13"
        assert vendr.failover_scraper == "KoolScraper"
