from .model import (
    Model,
    CharField,
    IntegerField,
    FloatField,
    RowData,
)
from .country_model import CountryModel
from .subdivision_model import SubdivisionModel
from ..dtos import SubdivisionBasic, Locality
from villager.utils import normalize, tokenize, extract_iso_code, parse_other_names
import sqlite3


class LocalityModel(Model[Locality]):
    table_name = "localities"
    dto_class = Locality

    name = CharField()
    population = IntegerField(index=False)
    lat = FloatField(index=False)
    lng = FloatField(index=False)
    country = CharField()
    country_alpha2 = CharField()
    country_alpha3 = CharField()
    subdivisions = CharField()

    @classmethod
    def parse_raw(cls, raw_data) -> dict | None:
        type = raw_data.get("type")
        population = raw_data.get("population") or None

        if type == "village" and population is None:
            return None

        # OSM
        osm_id = raw_data.get("osm_id")
        osm_type = raw_data.get("osm_type")

        if not osm_id or not osm_type:
            return None, None

        osm_type = osm_type[0]

        # Name
        name, other_names = parse_other_names(
            raw_data.get("name", None), raw_data.get("other_names", {})
        )
        if not name:
            return None

        # Address Data
        address: dict = raw_data.get("address", {})
        if not address:
            return None

        country_alpha2 = address.get("country_code")

        lng, lat = raw_data.get("location", (None, None))

        # Country
        country = CountryModel.get(CountryModel.alpha2 == country_alpha2)
        if not country:
            return None

        # Subdivisions

        def get_subdivisions(
            iso_code: str, subdivisions: list[SubdivisionBasic] = []
        ) -> list[SubdivisionBasic]:
            if not iso_code:
                return subdivisions

            sub = SubdivisionModel.get_by_iso_code(iso_code)
            if not sub:
                return subdivisions

            subdivisions.append(sub)
            return get_subdivisions(sub.parent_iso_code, subdivisions)

        sub_iso_code = extract_iso_code(address)
        subdivisions = get_subdivisions(sub_iso_code)
        if not subdivisions:
            return None

        subdivisions = " ".join(
            [f"{s.name} {s.code} {s.admin_level}" for s in subdivisions]
        )

        return {
            "name": name,
            "population": population,
            "lat": lat,
            "lng": lng,
            "country": country.name,
            "country_alpha2": country.alpha2,
            "country_alpha3": country.alpha3,
            "subdivisions": subdivisions,
        }

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
