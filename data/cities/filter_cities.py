from pathlib import Path
from dataclasses import dataclass
import json

BASE_PATH = Path(__file__).parent

index_map = {
    0: "geoname_id",
    1: "name",
    2: "ascii_name",
    3: "alt_names",
    4: "lat",
    5: "lng",
    6: "feature_class",
    7: "feature_code",
    8: "country_alpha2",
    9: "cc2",
    10: "admin1_code",
    11: "admin2_code",
    12: "admin3_code",
    13: "admin4_code",
    14: "population",
    15: "elevation",
    16: "dem",
    17: "timezone",
    18: "last_modified",
}


@dataclass
class CityDTO:
    name: str
    alt_names: list[str]
    lat: float
    lng: float
    country_alpha2: str
    admin1_code: str
    admin2_code: str
    admin3_code: str
    admin4_code: str
    population: int


def parse_geoname_line(line: str) -> tuple[CityDTO, str]:
    fields = line.strip().split("\t")
    if len(fields) != 19:
        raise ValueError(f"Expected 19 fields, got {len(fields)}")

    name = fields[1]
    alt_names = fields[3].split(",") if fields[3] else []
    ascii_name = fields[2]

    if name in alt_names:
        alt_names.remove(name)

    if ascii_name != name and ascii_name not in alt_names:
        alt_names.append(ascii_name)

    alt_names = "|".join(alt_names)

    lat = float(fields[4])
    lng = float(fields[5])

    country_alpha2 = fields[8]
    admin1_code = fields[10]
    admin2_code = fields[11]
    admin3_code = fields[12]
    admin4_code = fields[13]

    try:
        population = int(fields[14]) if fields[14] else 0
    except ValueError:
        raise ValueError(f"Invalid population value: {fields[14]}")

    feature_code = fields[7]

    return (
        CityDTO(
            name,
            alt_names,
            lat,
            lng,
            country_alpha2,
            admin1_code,
            admin2_code,
            admin3_code,
            admin4_code,
            population,
        ),
        feature_code,
    )


feature_codes = [
    "PPL",
    "PPLA",
    "PPLA2",
    "PPLA3",
    "PPLA4",
    "PPLA5",
    "PPLC",
    "PPLF",
    "PPLL",
    "PPLS",
    "STLMT",
]

cities = []

with open(BASE_PATH / "allCountries.txt", "r", encoding="utf-8") as f:
    for line in f:
        fields = line.split("\t")
        city, feature_code = parse_geoname_line(line)
        if feature_code in feature_codes and int(city.population) > 0:
            cities.append(city.__dict__)

with open(BASE_PATH / "cities_01.json", "w", encoding="utf-8") as f:
    json.dump(cities, f, indent=2, ensure_ascii=False)
