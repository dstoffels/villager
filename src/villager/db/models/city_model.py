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
    admin1 = CharField()
    admin2 = CharField()
    country = CharField()
    tokens = CharField()
    lat = FloatField(index=False)
    lng = FloatField(index=False)
    population = IntegerField(index=False)

    @classmethod
    def from_row(cls, row):
        sub_fields = row["subdivisions"].split(" ")
        subdivisions = []

        for i, field in enumerate(sub_fields):
            if i % 3 == 0:
                subdivisions.append(
                    SubdivisionBasic(
                        name=field,
                        code=sub_fields[i + 1],
                        admin_level=sub_fields[i + 2],
                    )
                )

        row["subdivisions"] = subdivisions

        return super().from_row(row)

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
