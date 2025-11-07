# This script aggregates country data from multiple sources and generates a TSV file containing country information such as ISO codes, names, and tokens for search optimization.
# Sources: ISO 3166 CSV, Wikidata JSON, GeoNames TXT

from pathlib import Path
import csv
import re
import json


BASE_PATH = Path(__file__).parent

from dataclasses import dataclass, field


# helper dto class
@dataclass
class CountryDTO:
    alpha2: str
    alpha3: str
    name: str = ""
    names: list[str] = field(default_factory=list)
    geonames_id: str = ""
    qid: str = ""
    fips: str = ""


countries: dict[str, CountryDTO] = {}


def init_iso_countries():
    with open(BASE_PATH / "source_data/iso_countries.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            country = CountryDTO(
                alpha2=row["#country_code_alpha2"],
                alpha3=row["country_code_alpha3"],
                name=row["name_short"],
            )

            country.names.append(row["name_long"])
            countries[country.alpha2] = country


def merge_wikidata():
    with open(
        BASE_PATH / "source_data/wiki_countries.json", "r", encoding="utf-8"
    ) as f:
        wiki_countries = json.load(f)
        for row in wiki_countries:
            alpha2 = row["alpha2"]
            if alpha2 not in countries:
                countries[alpha2] = CountryDTO(
                    alpha2=alpha2,
                    alpha3=row.get("alpha3", ""),
                    name=row.get("name", ""),
                )

            country: CountryDTO = countries.get(row["alpha2"])
            country.qid = row.get("qid", "")

            name = row.get("name", "")
            if name and name not in country.names:
                country.names.append(name)

            names: list[str] = row.get("aliases", "").split("|")
            country.names.extend(names)


def merge_geonames():
    with open(
        BASE_PATH / "source_data/geonames_countries.txt", "r", encoding="utf-8"
    ) as f:
        # #ISO	ISO3	ISO-Numeric	fips	Country	Capital	Area(in sq km)	Population	Continent	tld	CurrencyCode CurrencyName	Phone	Postal Code Format	Postal Code Regex	Languages	geonameid	neighbours	EquivalentFipsCode

        for line in f:
            parts = line.strip().split("\t")
            alpha2 = parts[0]
            alpha3 = parts[1]
            fips = parts[3]
            name = parts[4]
            geonames_id = parts[16]

            country: CountryDTO = countries.get(alpha2)
            if not country:
                continue

            country.alpha3 = alpha3
            country.fips = fips
            country.geonames_id = geonames_id

            if name and name not in country.names:
                country.names.append(name)


# deprecated. Too much noise in the alt names data

# def merge_alt_names():
#     with open(BASE_PATH.parent / "alts.tsv", "r", encoding="utf-8") as f:
#         data = csv.DictReader(f, delimiter="\t")
#         alts: dict[str, list[str]] = {a["id"]: a["alt_names"].split("|") for a in data}

#         for country in countries.values():
#             alt: list[str] = alts.get(country.geonames_id, None)
#             if not alt:
#                 continue

#             country.names.extend(alt)

#             # initial deduplication
#             country.names = list(set(country.names))

#             country_names = [name for name in country.names]
#             for name in country_names:
#                 name_lower = name.lower()
#                 if (
#                     "ISO 3166" in name
#                     or name_lower == country.alpha2.lower()
#                     or name_lower == country.alpha3.lower()
#                     or name_lower == country.name.lower()
#                     or name_lower == country.fips.lower()
#                     or any(n.lower() == name_lower for n in country.names if n != name)
#                 ):
#                     country.names.remove(name)


def parse_tokens(names: list[str], name: str) -> str:
    TOKEN_SPLIT_RE = re.compile(r"[\W_]+")
    STOPWORDS = {"the", "of", "and"}

    tokens: set[str] = set()

    for n in names:
        parts = TOKEN_SPLIT_RE.split(n.lower().strip())
        for p in parts:
            if p not in name.lower().split() and p not in STOPWORDS and len(p) > 2:
                tokens.add(p)

    return " ".join(sorted(tokens))


def build_row(country: CountryDTO) -> list[str]:
    return [
        country.geonames_id,
        country.name,
        country.alpha2,
        country.alpha3,
        parse_tokens(country.names, country.name),
    ]


def print_to_tsv():
    headers = ("id", "name", "alpha2", "alpha3", "tokens")
    rows: list[list[str]] = [build_row(c) for c in countries.values()]

    with open(BASE_PATH / "countries.tsv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)


def main():
    init_iso_countries()
    merge_wikidata()
    merge_geonames()
    # merge_alt_names()
    print_to_tsv()


main()
