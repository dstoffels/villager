from .model import Model, AutoField, CharField, IntegerField, Country
from villager.utils import normalize, tokenize
import sqlite3


class CountryModel(Model[Country]):
    table_name = "countries"
    dto_class = Country

    name = CharField()
    alpha2 = CharField()
    alpha3 = CharField()
    aliases = CharField()
    tokens = CharField()

    @classmethod
    def from_row(cls, row: sqlite3.Row):
        row = dict(row)
        aliases = row["aliases"].replace("|", " ") if row["aliases"] else ""
        cls.search_tokens = f'{row["name"]} {row["alpha2"]} {row["alpha3"]} {aliases} {row.pop("tokens")}'
        return super().from_row(row)

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
