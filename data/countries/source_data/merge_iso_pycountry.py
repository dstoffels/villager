# This script merges ISO country data using the pycountry library and outputs it to a single CSV file (iso_countries.csv) pycountry contains accurate official (long) names, which ISO 3166 may lack, and we account for some known naming discrepancies. The final result is a more

from pathlib import Path
import csv
import pycountry


BASE_PATH = Path(__file__).parent


pycountries: list[dict] = []

for country in pycountry.countries:
    pycountries.append(country._fields)

pycountries.sort(key=lambda c: c.get("alpha_2"))

with open(BASE_PATH / "iso_countries.csv", "w", encoding="utf-8", newline="") as f:
    headers = (
        "#country_code_alpha2",
        "country_code_alpha3",
        "numeric_code",
        "name_short",
        "name_long",
        "flag",
    )
    writer = csv.DictWriter(
        f,
        fieldnames=headers,
    )
    writer.writeheader()
    for country in pycountries:
        name = country.get("common_name") or country.get("name")
        name_map = {
            "CG": "Republic of the Congo",
            "CD": "Democratic Republic of the Congo",
            "FK": "Falkland Islands",
            "FM": "Micronesia",
            "MF": "Saint Martin",
            "SX": "Sint Maarten",
            "PS": "Palestine",
            "SH": "Saint Helena",
            "VA": "Holy See",
            "VG": "British Virgin Islands",
            "VI": "U.S. Virgin Islands",
            "VN": "Viet Nam",
        }
        name = name_map.get(country.get("alpha_2"), name)

        official_name_map = {
            "FK": "Falkland Islands (Malvinas)",
            "KR": "Republic of Korea",
            "LA": "Lao People's Democratic Republic",
            "MF": "Collectivity of Saint Martin",
            "SX": "Country of Sint Maarten",
            "SH": "Saint Helena, Ascension and Tristan da Cunha",
            "SY": "Syrian Arab Republic",
            "TW": "Republic of China",
            "VA": "Vatican City State",
        }

        long_name = country.get("official_name") or name
        long_name = official_name_map.get(country.get("alpha_2"), long_name)

        writer.writerow(
            {
                "#country_code_alpha2": country.get("alpha_2"),
                "country_code_alpha3": country.get("alpha_3"),
                "numeric_code": country.get("numeric"),
                "name_short": name,
                "name_long": long_name,
                "flag": country.get("flag"),
            }
        )
