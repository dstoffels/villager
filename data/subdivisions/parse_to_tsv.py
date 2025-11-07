import json
import csv
import re

from pathlib import Path

BASE_PATH = Path(__file__).parent

headers = (
    "id",
    "name",
    "code",
    "iso_code",
    "category",
    "parent_code",
    "country",
    "tokens",
)

TOKEN_SPLIT_RE = re.compile(r"[\W_]+")

STOPWORDS = {
    "the",
    "of",
    "and",
    "de",
    "di",
}

countries: dict[str, dict[str, str]] = {}
rows: list[list[str]] = []


def get_countries():
    with open(BASE_PATH.parent / "countries/countries.tsv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")

        for line in reader:
            countries[line["alpha2"]] = line


def parse_tokens(names: list[str], name: str, category: str) -> str:
    tokens: set[str] = set()

    for n in names:
        parts = TOKEN_SPLIT_RE.split(n.lower().strip())
        for p in parts:
            if (
                p not in name.lower().split()
                and p not in STOPWORDS
                and len(p) > 2
                and p not in category.lower()
            ):
                tokens.add(p)
    return " ".join(sorted(tokens))


def get_country(code: str) -> str:
    c = countries[code]
    return (
        f"{c['name']}|{c['alpha2']}{f'|{c.get('alpha3')}' if c.get('alpha3') else ''}"
    )


def build_row(line: dict[str, str | None | list[str]]) -> list[str]:
    return [
        line["geonames_id"],
        line["name"],
        line.get("geonames_code") or "",
        line["iso_code"],
        line["category"],
        line["parent_geonames_code"],
        get_country(line["country_alpha2"]),
        parse_tokens(line["names"], line["name"], line["category"]),
    ]


with open(BASE_PATH / "subdivisions_01.json", "r", encoding="utf-8") as f:
    get_countries()
    subdivisions: dict[str, dict[str, str | list[str]]] = json.load(f)
    for s in subdivisions.values():
        rows.append(build_row(s))

with open(BASE_PATH / "subdivisions.tsv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
