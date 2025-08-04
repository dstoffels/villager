from villager.db import db, CountryModel, SubdivisionModel, CityModel
import csv
from pathlib import Path
import hashlib
import zipfile
import json
import os


def run() -> None:
    db.create_tables([CountryModel, SubdivisionModel, CityModel])
    ingest_countries()
    ingest_subdivisions()
    ingest_localities()
    db.vacuum()
    compress_db(db.db_path)


DATA_DIR = Path(__file__).parent.parent / "data"


def chunked(list: list, size: int):
    for i in range(0, len(list), size):
        yield list[i : i + size]


def ingest_countries() -> None:
    countries: dict[str, dict] = {}

    with open(DATA_DIR / "countries.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for line in reader:
            country_dict = CountryModel.parse_raw(line)
            k = country_dict["alpha2"]
            if k not in countries:
                countries[k] = country_dict

    with db.atomic():
        for batch in chunked(list(countries.values()), 100):
            try:
                CountryModel.insert_many(batch)
            except Exception as e:
                print(f"Unexpected error on batch: {e}")
                raise e


def ingest_subdivisions() -> None:
    subdivisions: dict[str, dict] = {}

    with open(DATA_DIR / "subdivisions.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for line in reader:
            data = SubdivisionModel.parse_raw(line)
            a2 = data.get("country_alpha2")
            code = data.get("code")
            iso_code = f"{a2}-{code}"
            if iso_code not in subdivisions:
                subdivisions[iso_code] = data

        # assign admin levels
        def get_admin_level(
            iso_code: str, subdivisions: dict[str, dict], cache: dict[str, int]
        ) -> int:
            if iso_code in cache:
                return cache[iso_code]

            sub = subdivisions.get(iso_code)
            if not sub:
                return 1

            parent_code = sub.get("parent_iso_code")
            if not parent_code or parent_code == iso_code:
                cache[iso_code] = 1
                return 1

            level = get_admin_level(parent_code, subdivisions, cache) + 1
            cache[iso_code] = level
            return level

        admin_level_cache = {}

        for k, sub in subdivisions.items():
            sub["admin_level"] = get_admin_level(k, subdivisions, admin_level_cache)

    with db.atomic():
        for batch in chunked(list(subdivisions.values()), 100):
            try:
                SubdivisionModel.insert_many(batch)
            except Exception as e:
                print(f"Unexpected error on batch: {e}")
                raise e


def ingest_localities() -> None:
    locality_dir = DATA_DIR / "localities"

    localities: dict[str, dict] = {}

    valid_types = {
        "city",
        "town",
        "village",
        "administrative",
    }

    for c_dir in locality_dir.iterdir():
        if not c_dir.is_dir():
            continue

        for file in c_dir.iterdir():
            if not file.is_file():
                continue

            with file.open("r", encoding="utf-8") as f:
                for line in f:
                    try:
                        data: dict = json.loads(line)

                        type_ = data.get("type")
                        if type_ not in valid_types:
                            continue

                        data["type"] = type_

                        data = CityModel.parse_raw(data)

                        if data:
                            hash = hashlib.sha256(
                                f"{data.get('name').strip().lower()}{data.get('subdivisions')}".encode()
                            ).hexdigest()

                            if hash not in localities:
                                localities[hash] = data

                    except json.JSONDecodeError as e:
                        print(f"Error Decoding JSON: {e}")
                        continue
                    except Exception as e:
                        print(f"Unexpected error on line: {line}")
                        raise e

    with db.atomic():
        for batch in chunked(list(localities.values()), 1000):
            try:
                CityModel.insert_many(batch)
            except Exception as e:
                print(f"Unexpected error on batch: {e}")
                raise e


def compress_db(db_path: str | Path) -> Path:
    db_path = Path(db_path)
    if not db_path.exists():
        raise FileNotFoundError(f"Database file not found: {db_path}")

    with zipfile.ZipFile(
        "src/villager/db/villager_db.zip", "w", compression=zipfile.ZIP_DEFLATED
    ) as zipf:
        zipf.write(db_path, arcname=db_path.name)


if __name__ == "__main__":
    run()
