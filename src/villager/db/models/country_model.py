from .model import Model, AutoField, CharField, IntegerField, Country
from villager.utils import normalize, tokenize


class CountryModel(Model[Country]):
    table_name = "countries"
    dto_class = Country

    name = CharField()
    alpha2 = CharField()
    alpha3 = CharField()
    long_name = CharField()

    @classmethod
    def parse_raw(cls, raw_data):
        name = raw_data["name_short"]
        alpha2 = raw_data["#country_code_alpha2"]
        alpha3 = raw_data["country_code_alpha3"]

        long_name = raw_data["name_long"]
        long_name = long_name if long_name != name else None

        return {
            "name": raw_data["name_short"],
            "alpha2": alpha2,
            "alpha3": alpha3,
            "long_name": long_name,
        }
