########################################################################################################################
# IMPORTS

import logging

import requests

from ..params.nominatim import POSTCODES

########################################################################################################################
# CLASSES

logger = logging.getLogger(__name__)


class Nominatim:
    def __init__(self, endpoint):
        self.endpoint = endpoint

    def geocode(self, address):
        return requests.get(f"{self.endpoint}/?q={address}&format=json").json()

    def geocode_parsed(self, address):
        results = self.geocode(address)

        if results:
            return self.reverse_parsed(results[0]["lat"], results[0]["lon"])

    def reverse(self, lat, lon):
        return requests.get(f"{self.endpoint}/reverse?lat={lat}&lon={lon}&format=json").json()

    def reverse_parsed(self, lat, lon):
        raw_json = self.reverse(lat, lon).get("address", {})

        postcode = self.validate_postcode(raw_json.get("postcode"))
        district, quarter = self.get_district_quarter(raw_json)
        return {
            "country": raw_json.get("country"),
            "country_code": raw_json.get("country_code"),
            "state": raw_json.get("state"),
            "province": self.get_province_from_postcode(postcode),
            "city": self.get_attribute(raw_json, ["city", "town", "village"]),
            "postcode": postcode,
            "district": district,
            "quarter": quarter,
            "street": raw_json.get("road"),
            "number": raw_json.get("house_number"),
        }

    @staticmethod
    def validate_postcode(postcode):
        if postcode and len(postcode) == 5 and postcode[:2] in POSTCODES:
            return postcode

    @staticmethod
    def get_province_from_postcode(postcode):
        if postcode:
            return POSTCODES[postcode[:2]]

    @staticmethod
    def get_attribute(raw_json, keys):
        for key in keys:
            if key in raw_json:
                return raw_json[key]

    def get_district_quarter(self, raw_json):
        district = self.get_attribute(raw_json, ["city_district", "suburb", "borough"])
        quarter = self.get_attribute(raw_json, ["quarter", "neighbourhood"])

        if not district and quarter:
            district = quarter
            quarter = None

        return district, quarter


class NominatimInterface(Nominatim):
    def __init__(self, config):
        if "osm" in config:
            self.config = config["osm"]

            self.endpoint = self.config["nominatim_endpoint"]

        else:
            logger.warning("no osm section in config")

        super().__init__(self.endpoint)
