import csv
from pathlib import Path
import json
from villager.db import db, CountryModel, SubdivisionModel, LocalityModel
import re
from typing import Optional

DATA_DIR = Path(__file__).parent.parent / "data"


def run_all_loaders() -> None:
    """
    Connects to the database, runs the data loading functions sequentially,
    then closes the database connection.
    """

    load_countries()
    load_subdivisions()
    load_localities()


def chunked(iterable, size):
    for i in range(0, len(iterable), size):
        yield iterable[i : i + size]


def load_countries() -> None:
    db.create_tables([CountryModel], safe=True)
    countries = []

    with open(DATA_DIR / "countries.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            countries.append(
                {
                    "name": row["name_short"],
                    "alpha2": row["#country_code_alpha2"],
                    "alpha3": row["country_code_alpha3"],
                    "numeric": int(row["numeric_code"]),
                    "long_name": row["name_long"],
                }
            )

    with db.atomic():
        for batch in chunked(countries, 100):
            try:
                CountryModel.insert_many(batch).execute()
            except Exception as e:
                print(f"Unexpected error on batch: {e}")
                raise e


def load_subdivisions() -> None:
    db.create_tables([SubdivisionModel], safe=True)
    subdivisions = []

    with open(DATA_DIR / "subdivisions.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        iso_codes = set()

        for row in reader:
            iso_code = row.get("subdivision_code_iso3166-2", "")
            if iso_code in iso_codes:
                continue
            iso_codes.add(iso_code)

            country_code = row.get("#country_code_alpha2", "")
            country: CountryModel | None = CountryModel.get_or_none(
                CountryModel.alpha2 == country_code
            )
            country_name = country.name if country else ""
            country_alpha3 = country.alpha3 if country else ""

            subdivisions.append(
                {
                    "name": row["subdivision_name"],
                    "iso_code": iso_code,
                    "code": iso_code.split("-")[-1] if "-" in iso_code else iso_code,
                    "type": row["category"],
                    "country": country_name,
                    "country_code": country_code,
                    "country_alpha3": country_alpha3,
                    "alt_name": row["localVariant"],
                }
            )

    with db.atomic():
        for batch in chunked(subdivisions, 100):
            try:
                SubdivisionModel.insert_many(batch).execute()
            except Exception as e:
                print(f"Unexpected error on batch: {e}")
                raise e


def extract_iso_code(address: dict) -> Optional[str]:
    for key, value in address.items():
        if re.match(r"ISO3166-2-lvl\d+$", key):
            return value
    return None


def filter_locality_name(name: str) -> Optional[str]:
    if not name:
        return None

    disallowed_pattern = re.compile(r"[^a-zA-Z\u00C0-\u00FF\u0100-\u017F \-']")

    if disallowed_pattern.search(name):
        return None

    return name.strip()


def load_localities() -> None:
    db.create_tables([LocalityModel], safe=True)
    locality_dir = DATA_DIR / "localities"
    localities = []
    country_map = {c.alpha2: c for c in CountryModel.select()}
    sub_map = {s.iso_code: s for s in SubdivisionModel.select()}

    for country_dir in locality_dir.iterdir():
        if not country_dir.is_dir():
            continue

        for file in country_dir.iterdir():
            if not file.is_file():
                continue

            # Skip hamlet files
            if "hamlet" in file.stem.lower():
                continue

            classification = file.stem.replace("place-", "")

            with file.open("r", encoding="utf-8") as f:
                for line in f:
                    try:
                        data: dict = json.loads(line)
                        name = filter_locality_name(data.get("name"))
                        if not name:
                            continue

                        address: dict = data.get("address", {})
                        if not address:
                            continue

                        lng, lat = data.get("location", (None, None))
                        admin1_iso_code = extract_iso_code(address)
                        admin1: SubdivisionModel = sub_map.get(admin1_iso_code)

                        country: CountryModel = country_map.get(
                            address.get("country_code", "").upper()
                        )

                        if not admin1:
                            continue

                        localities.append(
                            {
                                "name": name,
                                "display_name": data.get("display_name"),
                                "admin1": admin1.name,
                                "admin1_iso_code": admin1.iso_code,
                                "admin1_code": admin1.code,
                                "country": address.get("country"),
                                "country_alpha2": country.alpha2,
                                "country_alpha3": country.alpha3,
                                "lat": lat,
                                "lng": lng,
                                "classification": classification,
                                "osm_type": data.get("osm_type"),
                                "osm_id": data.get("osm_id"),
                                "population": data.get("population", None),
                            }
                        )

                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON: {e}")
                        continue
                    except Exception as e:
                        print(f"Unexpected error on line: {line}")
                        raise e

    with db.atomic():
        for batch in chunked(localities, 100):
            try:
                LocalityModel.insert_many(batch).execute()
            except Exception as e:
                print(f"Unexpected error on batch: {e}")
                raise e


if __name__ == "__main__":
    run_all_loaders()
