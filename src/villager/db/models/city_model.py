from .model import (
    Model,
    CharField,
    IntegerField,
    FloatField,
    RowData,
)
from .country_model import CountryModel
from .subdivision_model import SubdivisionModel
from ..dtos import SubdivisionBasic, City
from villager.utils import normalize, tokenize, extract_iso_code, parse_other_names
import sqlite3


class CityModel(Model[City]):
    table_name = "cities"
    dto_class = City

    name = CharField()
    alt_names = CharField()
    admin1 = CharField()
    admin2 = CharField()
    country = CharField()
    population = IntegerField(index=False)
    lat = FloatField(index=False)
    lng = FloatField(index=False)

    @classmethod
    def from_row(cls, row: sqlite3.Row):
        row: dict = dict(row)
        subdivisions: list[SubdivisionBasic] = []
        admin1: str = row["admin1"]
        if admin1:
            name, code = admin1.split("|")
            code_parts = code.split(".")
            code = code_parts[len(code_parts) - 1]
            subdivisions.append(SubdivisionBasic(name, code, 1))
        admin2: str = row["admin2"]
        if admin2:
            name, code = admin2.split("|")
            code_parts = code.split(".")
            code = code_parts[len(code_parts) - 1]
            subdivisions.append(SubdivisionBasic(name, code, 2))
        row["subdivisions"] = subdivisions

        country_parts = row["country"].split("|")

        if len(country_parts) == 2:
            country, alpha2 = country_parts
        else:
            country, alpha2, alpha3 = country_parts

        row["country"] = country
        row["country_alpha2"] = alpha2
        row["country_alpha3"] = alpha3

        row["display_name"] = (
            f"{row['name']}{(", " + subdivisions[1].name) if admin2 else ""}{(', ' + subdivisions[0].name) if admin1 else""}, {country}"
        )

        cls.search_tokens = f'{row['name']} {f" ".join([f'{s.name} {s.code}' for s in subdivisions])} {country} {alpha2} {alpha3} {row.pop('tokens')}'

        return super().from_row(row)

    @classmethod
    def get_search_tokens(cls, row: dict):
        return

    @classmethod
    def get_subdivisions(cls, row: sqlite3.Row) -> list[SubdivisionBasic]:
        subdivisions: list[SubdivisionBasic] = []
        admin1: str = row["admin1"]
        if admin1:
            name, code = admin1.split("|")
            code_parts = code.split(".")
            code = code_parts[len(code_parts) - 1]
            subdivisions.append(SubdivisionBasic(name, code, 1))
        admin2: str = row["admin2"]
        if admin2:
            name, code = admin2.split("|")
            code_parts = code.split(".")
            code = code_parts[len(code_parts) - 1]
            subdivisions.append(SubdivisionBasic(name, code, 2))
        return subdivisions

    # @classmethod
    # def from_row(cls, row: sqlite3.Row) -> RowData[Locality]:
    #     data = {k: row[k] for k in row.keys() if k in cls.dto_class.__annotations__}
    #     id = row["id"]
    #     tokens = row["tokens"]

    #     subdivisions = []
    #     if row["sub1_name"]:
    #         subdivisions.append(
    #             SubdivisionBasic(
    #                 name=row["sub1_name"],
    #                 iso_code=row["sub1_iso_code"],
    #                 code=row["sub1_code"],
    #                 category=row["sub1_category"],
    #                 admin_level=row["sub1_admin_level"],
    #             )
    #         )

    #     if row["sub2_name"]:
    #         subdivisions.append(
    #             SubdivisionBasic(
    #                 name=row["sub2_name"],
    #                 iso_code=row["sub2_iso_code"],
    #                 code=row["sub2_code"],
    #                 category=row["sub2_category"],
    #                 admin_level=row["sub2_admin_level"],
    #             )
    #         )
    #     data["villager_id"] = f'{row["osm_type"]}:{row["osm_id"]}'
    #     data["subdivisions"] = subdivisions
    #     data["display_name"] = (
    #         f'{row["name"]}, {row['sub1_name']}, {f'{row["sub2_name"]}, ' if row['sub2_name'] else ""}{row["country"]}'
    #     )
    #     return RowData(id, cls.dto_class(**data), tokens)
