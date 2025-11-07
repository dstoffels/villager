import csv
import json
from ..countries.country_dto import CountryDTO
from .subdivision_dto import SubdivisionDTO
from rapidfuzz import fuzz
import unicodedata
from unidecode import unidecode


from pathlib import Path

BASE_PATH = Path(__file__).parent

# initialize with geoname
subs_by_country: dict[str, dict[str, SubdivisionDTO]] = {}
subs_by_id: dict[str, SubdivisionDTO] = {}

# get countries
countries: dict[str, CountryDTO] = {}
with open(BASE_PATH.parent / "countries/countries.json", "r", encoding="utf-8") as f:
    countries = {k: CountryDTO(**v) for k, v in json.load(f).items()}


def parse_geonames_file(file_name: Path):
    with open(BASE_PATH / file_name, "r", encoding="utf-8") as f:
        for line in f:
            # code, name, name_ascii, geonames_id
            parts = line.strip().split("\t")
            geonames_code = parts[0]
            code_parts = geonames_code.split(".")

            if len(code_parts) == 2:
                country_alpha2, code = code_parts
                parent_code = None
            elif len(code_parts) == 3:
                country_alpha2, parent_code, code = code_parts
                parent_code = f"{country_alpha2}.{parent_code}"

            country = countries.get(country_alpha2)
            if not country:
                raise ValueError(f"Country not found for alpha2: {country_alpha2}")

            name = parts[1]
            alt_name = parts[2] if parts[2] != name else None
            geonames_id = parts[3]

            subdivision = SubdivisionDTO(
                name=name,
                country_alpha2=country.alpha2,
                country_alpha3=country.alpha3,
                country_name=country.name,
                geonames_id=geonames_id,
                geonames_code=geonames_code,
                parent_geonames_code=parent_code,
            )

            if alt_name and alt_name not in subdivision.names:
                subdivision.names.append(alt_name)

            if country_alpha2 not in subs_by_country:
                subs_by_country[country_alpha2] = {}
            country_map: dict[str, SubdivisionDTO] = subs_by_country[country_alpha2]

            if subdivision.geonames_code not in country_map:
                country_map[subdivision.geonames_code] = subdivision

            else:
                raise ValueError(
                    f"Duplicate subdivision code: {subdivision.geonames_code}"
                )
            if subdivision.geonames_id not in subs_by_id:
                subs_by_id[subdivision.geonames_id] = subdivision


parse_geonames_file("admin1.txt")
parse_geonames_file("admin2.txt")


def dedupe(l: list) -> list:
    return sorted(list(set(l)))


# merge with alt names
with open(BASE_PATH.parent / "alts.json", "r", encoding="utf-8") as f:
    alts: dict[str, dict] = json.load(f)

    for sub in subs_by_id.values():
        alt: dict[str, str | None | list[str]] = alts.get(sub.geonames_id, None)
        if not alt:
            continue
        preferred = alt.get("preferred")
        if preferred and preferred != sub.name:
            sub.names.append(sub.name)
            sub.name = preferred
        sub.names.extend(alt.get("names", []))

        # initial deduplication
        sub.names = dedupe(sub.names)


def normalize(s: str) -> str:
    MAP = {"ə": "a", "ǝ": "ä"}

    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = "".join(MAP.get(ch, ch) for ch in s)
    s = unidecode(s)
    return s.strip()


# init ISO 3166-2
iso_subs: dict[str, SubdivisionDTO] = {}

with open(BASE_PATH / "iso-3166-2.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        iso_name = row["name"]
        ascii_name = normalize(iso_name).title()
        alt_name = row["localVariant"]
        alpha2 = row["country_code"]
        iso_code = row["iso_code"]
        code = iso_code.replace("-", ".")

        country = countries.get(alpha2)
        if not country:
            raise ValueError(f"Country not found for alpha2: {alpha2}")

        # new subdivision
        if code not in iso_subs:
            new_sub = SubdivisionDTO(
                name=iso_name,
                country_alpha2=country.alpha2,
                country_alpha3=country.alpha3,
                country_name=country.name,
                geonames_id=None,
                geonames_code=None,
                parent_geonames_code=None,
                category=row["category"],
                iso_code=iso_code,
            )

            # add names regardless of duplicates for easier matching, dedupe later
            new_sub.names.append(iso_name)
            new_sub.names.append(ascii_name)
            if alt_name:
                new_sub.names.append(alt_name)
            iso_subs[code] = new_sub
        else:
            # add other names to existing subdivision
            existing_sub = iso_subs[code]
            if iso_name not in existing_sub.names:
                existing_sub.names.append(iso_name)
            if alt_name and alt_name not in existing_sub.names:
                existing_sub.names.append(alt_name)


THRESHOLD = 90

DIRECTIONAL_TOKENS = {
    "north",
    "south",
    "east",
    "west",
    "northern",
    "southern",
    "eastern",
    "western",
    "upper",
    "lower",
    "central",
}

CATEGORICAL_TOKENS = {
    "okrug",
    "oblast",
    "kray",
    "kraj",
    "lan",
    "län",
    "rayon",
    "comuna",
    "district",
    "province",
    "region",
    "state",
    "shi",
    "sheng",
}
import re


def strip_cat_tokens(s: str) -> str:
    tokens = re.split(r"\W+", s.lower())
    filtered = [t for t in tokens if t and t not in CATEGORICAL_TOKENS]
    return " ".join(filtered)


def has_directional_mismatch(name1: str, name2: str) -> bool:
    tokens1 = set(name1.lower().split())
    tokens2 = set(name2.lower().split())
    return any(t in tokens1 ^ tokens2 for t in DIRECTIONAL_TOKENS)


def merge_subdivision(iso_sub: SubdivisionDTO, geo_sub: SubdivisionDTO) -> None:
    geo_sub.category = iso_sub.category
    geo_sub.iso_code = iso_sub.iso_code
    if iso_sub.name not in geo_sub.names:
        geo_sub.names.append(iso_sub.name)
    geo_sub.names.extend(iso_sub.names)
    geo_sub.names = dedupe(geo_sub.names)


def resolve_subdivision(
    iso_sub: SubdivisionDTO, candidate_geo_subs: list[SubdivisionDTO], num: int
) -> dict | None:

    candidate_geo_subs = sorted(candidate_geo_subs, key=lambda x: x.name)
    print("Candidates:")
    for i, geo_sub in enumerate(candidate_geo_subs):
        print(
            f"{i + 1}. {[geo_sub.name, *geo_sub.names]} (Code: {geo_sub.geonames_code})"
        )

    print(f"Manually resolve subdivision ({n}/{len(unmatched)}):")
    print([iso_sub.name, *iso_sub.names], f"(ISO Code: {iso_sub.iso_code})")
    choice = input(
        f"""Select a candidate by number to merge with {iso_sub.name}.
Enter 'a' to add {iso_sub.name} as-is.
Enter 'e' to add names to {iso_sub.name}.
"""
    )

    choice = choice.lower()
    if choice == "a":
        iso_sub.geonames_code = iso_sub.iso_code.replace("-", ".")
        subs_by_country[iso_sub.country_alpha2][iso_sub.iso_code] = iso_sub
    elif choice == "e":
        while True:
            new_name = input(f'Enter a new name or "EXIT" to return: ')
            if new_name == "EXIT":
                resolve_subdivision(iso_sub, candidate_geo_subs, num)
                break
            iso_sub.names.append(new_name)
    elif choice.isdigit() and 1 <= int(choice) <= len(candidate_geo_subs):
        selected_geo_sub = candidate_geo_subs[int(choice) - 1]
        merge_subdivision(iso_sub, selected_geo_sub)
        print(json.dumps(selected_geo_sub.__dict__))


unmatched: list[SubdivisionDTO] = []


# merge ISO 3166-2 with geonames subdivisions
for code, iso_sub in iso_subs.items():
    iso_sub.names = dedupe(iso_sub.names)
    country_map = subs_by_country.get(iso_sub.country_alpha2, None)
    if not country_map:
        subs_by_country[iso_sub.country_alpha2] = {}
        country_map = subs_by_country[iso_sub.country_alpha2]
        country_map[code] = iso_sub
        continue

    # code match found
    if code in country_map:
        geo_sub = country_map[code]
        merge_subdivision(iso_sub, geo_sub)
    else:
        # no code match, try to match by name
        match_found = False
        for geo_sub in country_map.values():
            geo_names = [geo_sub.name, *geo_sub.names]

            # compare each name in iso_sub with each name in geo_sub
            for iso_name in iso_sub.names:
                for geo_name in geo_names:
                    if fuzz.token_set_ratio(
                        normalize(strip_cat_tokens(iso_name)),
                        normalize(strip_cat_tokens(geo_name)),
                    ) > THRESHOLD and not has_directional_mismatch(iso_name, geo_name):
                        # match found
                        merge_subdivision(iso_sub, geo_sub)
                        match_found = True
                        break
                if match_found:
                    break
            if match_found:
                break
        if not match_found:
            unmatched.append(iso_sub)

# manually merge unmatched
for n, iso_sub in enumerate(unmatched, 1):
    resolve_subdivision(
        iso_sub, list(subs_by_country[iso_sub.country_alpha2].values()), n
    )


with open(BASE_PATH / "subdivisions.json", "w", encoding="utf-8") as f:
    flatmap = {
        sub.geonames_code: sub.__dict__
        for country_map in subs_by_country.values()
        for sub in country_map.values()
    }
    json.dump(flatmap, f, indent=2, ensure_ascii=False)
