from .model import (
    Model,
    AutoField,
    CharField,
    IntegerField,
    ForeignKeyField,
    Subdivision,
    SubdivisionBasic,
)
from .country_model import CountryModel
from villager.utils import normalize, tokenize


class SubdivisionModel(Model[Subdivision]):
    table_name = "subdivisions"
    dto_class = Subdivision

    name = CharField()
    code = CharField()
    category = CharField()
    parent_iso_code = CharField()
    admin_level = IntegerField(default=1)
    aliases = CharField()
    country = CharField()
    country_alpha2 = CharField()
    country_alpha3 = CharField()

    @classmethod
    def parse_raw(cls, raw_data):
        country = CountryModel.get(CountryModel.alpha2 == raw_data["country_alpha2"])

        return {
            **raw_data,
            "country": country.name,
            "country_alpha2": country.alpha2,
            "country_alpha3": country.alpha3,
        }

    @classmethod
    def from_row(cls, row):
        row = dict(row)

        row["iso_code"] = f'{row["country_alpha2"]}-{row["code"]}'

        subs = SubdivisionModel.select(
            SubdivisionModel.parent_iso_code == row["iso_code"]
        )
        row["subdivisions"] = []
        for s in subs:
            row["subdivisions"].append(
                SubdivisionBasic(name=s.name, code=s.code, admin_level=s.admin_level)
            )

        row["aliases"] = [a for a in row["aliases"].split("|")]
        return super().from_row(row)

    @classmethod
    def get_by_iso_code(cls, iso_code: str) -> Subdivision:
        alpha2, *code = tuple(iso_code.split("-"))
        code = "-".join([*code])
        return cls.get((cls.country_alpha2 == alpha2) & (cls.code == code))
