import json
import time
import requests
from pathlib import Path
import csv
from dataclasses import dataclass
from rapidfuzz import fuzz
import unicodedata

BASE_PATH = Path(__file__).parent


@dataclass
class sub_txt:
    code: str
    name: str
    name_ascii: str
    geoname_id: int


def parse_sub(line: str) -> sub_txt:
    fields = line.split("\t")
    return sub_txt(*fields)


def parse_raw() -> dict:
    subs_by_country = {}
    with open(BASE_PATH / "subdivisions_raw.json", "r", encoding="utf-8") as raw:
        raw_data: dict = json.load(raw)
        print(len(raw_data))
        for k, s in raw_data.items():
            name = s.get("name") or s.get("subdivision_name")
            cat = s["category"].title()
            parent = s["parent_subdivision"] or None
            country = s["#country_code_alpha2"]

            aliases = []
            for a in s.get("aliases", []):
                if name.lower() in a.lower():
                    continue
                if cat.lower() in a.lower():
                    a = a.replace(cat.lower(), "").strip()
                    a = a.replace(cat.upper(), "").strip()
                    a = a.replace(cat.title(), "").strip()
                aliases.append(a)

            alias = s.get("subdivision_name")

            if alias and alias != name:
                aliases.append(alias)

            local_variant = s.get("localVariant")
            if local_variant and local_variant != name:
                aliases.append(local_variant)

            sub = {
                "name": name,
                "code": k.split("-")[1],
                "category": cat,
                "parent_iso_code": parent,
                "admin_level": 1,
                "country_alpha2": s["#country_code_alpha2"],
                "aliases": "|".join(aliases),
            }

            if country not in subs_by_country:
                subs_by_country[country] = {}
            subs_by_country[country][f"{country}.{sub['code']}"] = sub
    return subs_by_country


def extract_codes(code: str) -> tuple[str, str, str]:
    parts = code.split(".")
    return parts[0], f"{parts[0]}-{parts[1]}", parts[2]


def parse_geonames(subs_by_country: dict[str, dict], filename: str):
    MATCH_THRESHOLD = 70
    matched = {}
    unmatched = {}
    with open(BASE_PATH / filename, "r", newline="", encoding="utf-8") as f:
        count = 0
        for line in f:
            count += 1

            geo_sub = parse_sub(line)

            name = geo_sub.name.lower()

            country, admin1 = geo_sub.code.split(".")[:2]

            submap = subs_by_country.get(country)
            if not submap:
                continue

            if geo_sub.code in submap:
                matched[geo_sub.code] = submap[geo_sub.code]
                continue

            match_flag = False
            for iso_code, sub in submap.items():
                norm_name = unicodedata.normalize("NFKD", geo_sub.name)
                norm_ascii_name = unicodedata.normalize("NFKD", geo_sub.name_ascii)
                norm_subname = unicodedata.normalize("NFKD", sub["name"])
                if fuzz.partial_token_ratio(norm_name, norm_subname) > MATCH_THRESHOLD:
                    matched[geo_sub.code] = sub
                    match_flag = True
                    break
                elif (
                    fuzz.partial_token_ratio(norm_ascii_name, norm_subname)
                    > MATCH_THRESHOLD
                ):
                    matched[geo_sub.code] = sub
                    match_flag = True
                    break
                elif sub["aliases"]:
                    for a in sub["aliases"].split("|"):
                        norm_alias = unicodedata.normalize("NFKD", a)
                        if (
                            fuzz.partial_token_ratio(norm_name, norm_alias)
                            > MATCH_THRESHOLD
                        ):
                            matched[geo_sub.code] = sub
                            match_flag = True
                            break
                        elif (
                            fuzz.partial_token_ratio(norm_ascii_name, norm_alias)
                            > MATCH_THRESHOLD
                        ):
                            matched[geo_sub.code] = sub
                            match_flag = True
                            break

                # sub_name = sub["name"].lower()
                # if (
                #     name in sub_name
                #     or sub_name in name
                #     or geo_sub.name_ascii.lower() in sub_name
                #     or sub_name in geo_sub.name_ascii.lower()
                # ):
                #     matched[geo_sub.code] = sub
                #     match_flag = True
                #     break
                # elif sub["aliases"]:
                #     aliases = sub["aliases"].lower().split("|")
                #     if any(name in alias for alias in aliases):
                #         matched[geo_sub.code] = sub
                #         match_flag = True
                #         break
                # elif (
                #     fuzz.ratio(name, sub_name) > 70
                #     or fuzz.ratio(geo_sub.name_ascii, sub_name) > 70
                # ):
                #     matched[geo_sub.code] = sub
                #     match_flag = True
                #     break

            if not match_flag:
                unmatched[geo_sub.code] = geo_sub.__dict__

    print(count)
    return matched, unmatched


def parse_admin2(subs: dict):
    with open(BASE_PATH / "admin2.txt", "r", newline="", encoding="utf-8") as admin2:
        for line in admin2:
            raw_sub = parse_sub(line)
            country_code, parent_code, code = extract_codes(raw_sub.code)

            if parent_code in subs:
                sub = {
                    "name": raw_sub.name,
                    "code": code,
                    "category": None,
                    "parent_iso_code": parent_code or None,
                    "admin_level": 1,
                    "country_alpha2": country_code,
                    "aliases": None,
                }

                subs[raw_sub.code.replace(".", "-")] = sub

    return subs


def set_admin_levels(subs: dict) -> None:
    def resolve_level(code: str, visited: set[str] = None) -> int:
        if visited is None:
            visited = set()
        if code in visited:
            # Circular ref guard
            return 0
        visited.add(code)

        sub = subs.get(code)
        if not sub:
            return 0
        parent_code = sub.get("parent_iso_code")
        if not parent_code or parent_code not in subs:
            return 1  # top-level
        parent_level = resolve_level(parent_code, visited)
        return parent_level + 1

    for code, sub in subs.items():
        sub["admin_level"] = resolve_level(code)


def main():
    subs_by_country = parse_raw()
    matched, unmatched = parse_geonames(subs_by_country, "admin1.txt")
    print(len(unmatched))
    # subs = parse_admin2(subs)

    # set_admin_levels(subs)

    with open(BASE_PATH / "subs_by_country.json", "w", encoding="utf-8") as f:
        json.dump(subs_by_country, f, indent=2, ensure_ascii=False)
    with open(BASE_PATH / "subdivisions.json", "w", encoding="utf-8") as f:
        json.dump(matched, f, indent=2, ensure_ascii=False)

    with open(BASE_PATH / "unmatched.json", "w", encoding="utf-8") as f:
        json.dump(unmatched, f, indent=2, ensure_ascii=False)


main()


# GEONAMES_COLUMNS = [
#     "geoname_id",
#     "name",
#     "ascii_name",
#     "aliases",
#     "lat",
#     "lng",
#     "feature_class",
#     "feature_code",
#     "country_code",
#     "cc2",
#     "admin1_code",
#     "admin2_code",
#     "admin3_code",
#     "admin4_code",
#     "population",
#     "elevation",
#     "dem",
#     "timezone",
#     "modification_date",
# ]


# def parse_geoname_line(line: str) -> dict:
#     fields = line.strip().split("\t")
#     if len(fields) != len(GEONAMES_COLUMNS):
#         raise ValueError(f"Expected {len(GEONAMES_COLUMNS)} fields, got {len(fields)}")

#     result = dict(zip(GEONAMES_COLUMNS, fields))

#     country_code = result["country_code"]

#     result["geoname_id"] = int(result["geoname_id"])
#     result["lat"] = float(result["lat"])
#     result["lng"] = float(result["lng"])
#     result["population"] = int(result["population"] if result["population"] else None)

#     alt_names = result["aliases"].split(",") if result["aliases"] else []

#     if result["name"] in alt_names:
#         alt_names.remove(result["name"])

#     if result["ascii_name"] != result["name"] and result["ascii_name"] not in alt_names:
#         alt_names.append(result["ascii_name"])

#     result["aliases"] = "|".join(alt_names)

#     result.pop("geoname_id")
#     result.pop("ascii_name")
#     result.pop("feature_class")
#     result.pop("feature_code")
#     result.pop("cc2")
#     result.pop("elevation")
#     result.pop("dem")
#     result.pop("timezone")
#     result.pop("modification_date")
#     result.pop("admin3_code")
#     result.pop("admin4_code")

#     return result


# def main():
#     with open(BASE_PATH / "cities500.txt", newline="", encoding="utf-8") as f:
#         locs = []
#         for line in f:
#             loc = parse_geoname_line(line)
#             locs.append(loc)

#         print(len(locs))

#     with open(BASE_PATH / "cities.json", "w", encoding="utf-8") as j:
#         json.dump(locs, j, indent=2, ensure_ascii=False)


# main()
