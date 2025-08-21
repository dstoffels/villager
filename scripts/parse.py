from pathlib import Path
import json
from dataclasses import dataclass

DIR = Path(__file__).parent
dest = DIR / "cities500.json"


@dataclass
class City:
    id: int
    geonameid: int
    name: str
    asciiname: str
    alternate_names: str
    latitude: float
    longitude: float
    feature_class: str
    feature_code: str
    country_code: str
    cc2: str
    admin1_code: str
    admin2_code: str
    admin3_code: str
    admin4_code: str
    population: int
    elevation: int
    dem: int
    timezone: str
    modification_date: str

    def to_dict(self):
        return self.__dict__


cities: list[City] = []

with open(DIR / "cities500.txt", "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        data = line.split("\t")

        try:
            city = City(
                id=i,
                geonameid=int(data[0]),
                name=data[1],
                asciiname=data[2],
                alternate_names=data[3].split(",") or None,
                latitude=float(data[4]),
                longitude=float(data[5]),
                feature_class=data[6],
                feature_code=data[7],
                country_code=data[8],
                cc2=data[9],
                admin1_code=data[10],
                admin2_code=data[11],
                admin3_code=data[12],
                admin4_code=data[13],
                population=int(data[14]),
                elevation=int(data[15]) if data[15] else None,
                dem=int(data[16]),
                timezone=data[17],
                modification_date=data[18],
            )
            cities.append(city.to_dict())
        except ValueError as e:
            print(f"Skipping line due to error: {e}")

with open(dest, "w", encoding="utf-8") as f:
    json.dump(cities, f, ensure_ascii=False, indent=2)
