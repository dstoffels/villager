# This patch reassigns the most canonical names to each subdivision based on the following priority:
# 1. iso 3166-2 localVariant if existent
# 2. iso 3166-2 subdivision_name if existent
# 3. geonames admin1CodesASCII.txt/admin2Codes.txt name

import json
import csv
import re

from pathlib import Path

BASE_PATH = Path(__file__).parent


iso_subs: dict[str, dict[str, str | list[str]]] = {}
geo_subs: dict[str, dict[str, str | list[str]]] = {}
subdivisions: dict[str, dict[str, str | list[str]]] = {}


def get_iso_subs():
    with open(BASE_PATH / "iso-3166-2.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            iso_subs[row["iso_code"]] = row


def get_geo_subs(filename: str):
    with open(BASE_PATH / filename, "r", encoding="utf-8") as f:
        for line in f:
            # code, name, name_ascii, geonames_id
            parts = line.strip().split("\t")
            geo_subs[parts[0]] = {
                "code": parts[0],
                "name": parts[1],
                "name_ascii": parts[2],
                "geonames_id": parts[3],
            }


def rename_subs():
    with open(BASE_PATH / "subdivisions.json", "r", encoding="utf-8") as f:
        subs: dict[str, dict[str, str | list[str]]] = json.load(f)
        for k, s in subs.items():
            current_name: str = s.get("name")

            iso_code: str = s.get("iso_code") or None
            iso_sub: dict[str, str | list[str]] = (
                iso_subs.get(iso_code, {}) if iso_code is not None else {}
            )
            iso_name: str = iso_sub.get("name", "")
            iso_localVariant: str = iso_sub.get("localVariant", "")

            geo_code: str = s.get("geonames_code", "")
            geo_sub: dict[str, str | list[str]] = geo_subs.get(geo_code, {})
            geo_name: str = geo_sub.get("name")

            if iso_localVariant:
                s["name"] = iso_localVariant
            elif iso_name:
                s["name"] = iso_name
            elif geo_sub and geo_name != current_name:
                s["names"].append(s["name"])
                s["name"] = geo_name

            subdivisions[k] = s


with open(BASE_PATH / "subdivisions_01.json", "w", encoding="utf-8", newline="") as f:
    get_iso_subs()
    get_geo_subs("admin1.txt")
    get_geo_subs("admin2.txt")
    rename_subs()
    json.dump(subdivisions, f, indent=2, ensure_ascii=False)
