from .model import Model, AutoField, CharField, IntegerField, Country
from villager.utils import normalize, tokenize


class CountryModel(Model[Country]):
    table_name = "countries"
    dto_class = Country
    base_query = "SELECT c.*, f.tokens as tokens FROM countries_fts f JOIN countries c ON f.rowid = c.id\n"

    id = AutoField()
    name = CharField(index=True, nullable=False)
    normalized_name = CharField(index=True, nullable=False)
    alpha2 = CharField(unique=True, index=True)
    alpha3 = CharField(unique=True, index=True)
    numeric = IntegerField(unique=True)
    long_name = CharField()

    @classmethod
    def parse_raw(cls, raw_data):
        base = {
            "name": raw_data["name_short"],
            "normalized_name": normalize(raw_data["name_short"]),
            "alpha2": raw_data["#country_code_alpha2"],
            "alpha3": raw_data["country_code_alpha3"],
            "numeric": int(raw_data["numeric_code"]),
            "long_name": raw_data["name_long"],
        }

        fts = {
            "tokens": tokenize(
                raw_data["name_short"],
                raw_data["#country_code_alpha2"],
                raw_data["country_code_alpha3"],
            )
        }
        return base, fts
