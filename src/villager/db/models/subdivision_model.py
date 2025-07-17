from .model import (
    Model,
    AutoField,
    CharField,
    IntegerField,
    ForeignKeyField,
    Subdivision,
)
from .country_model import CountryModel
from villager.utils import normalize, tokenize


class SubdivisionModel(Model[Subdivision]):
    table_name = "subdivisions"
    dto_class = Subdivision

    name = CharField()
    alt_name = CharField()
    code = CharField()
    category = CharField()
    parent_iso_code = CharField()
    admin_level = IntegerField(default=1)
    country = CharField()
    country_alpha2 = CharField()
    country_alpha3 = CharField()

    @classmethod
    def parse_raw(cls, raw_data):
        country = CountryModel.get(
            CountryModel.alpha2 == raw_data["#country_code_alpha2"]
        )

        iso_code: str = raw_data["subdivision_code_iso3166-2"]

        name = raw_data["subdivision_name"]

        return {
            "name": name,
            "code": iso_code.split("-")[-1],
            "category": raw_data.get("category") or None,
            "alt_name": raw_data.get("localVariant") or None,
            "parent_iso_code": raw_data.get("parent_subdivision") or None,
            "admin_level": 1,
            "country": country.name,
            "country_alpha2": country.alpha2,
            "country_alpha3": country.alpha3,
        }

    @classmethod
    def from_row(cls, row):
        row = dict(row)

        row["iso_code"] = f'{row["country_alpha2"]}-{row["code"]}'

        return super().from_row(row)
    
    @classmethod
    def get_by_iso_code(cls, iso_code: str) -> Subdivision:
        alpha2, *code = tuple(iso_code.split("-"))
        code = "-".join([*code])
        return cls.get(
            (cls.country_alpha2 == alpha2) & (cls.code == code)
        )
