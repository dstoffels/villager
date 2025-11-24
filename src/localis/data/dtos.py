# These DTOS are the final product delivered to the user.

from __future__ import annotations
from dataclasses import dataclass, asdict
import json
from abc import ABC


@dataclass(slots=True)
class DTO(ABC):
    id: int
    name: str

    def to_dict(self, depth: int = 1):
        return asdict(self)

    def json(self):
        return json.dumps(self.to_dict(), indent=2)

    def __str__(self):
        return self.json()


@dataclass(slots=True)
class Country(DTO):
    id: int
    name: str
    official_name: str
    alt_names: list[str]
    alpha2: str
    alpha3: str
    numeric: int
    flag: str

    def to_dict(self, depth=1):
        data = {
            "id": self.id,
            "name": self.name,
            "official_name": self.official_name,
            "alpha2": self.alpha2,
            "alpha3": self.alpha3,
            "numeric": self.numeric,
            "flag": self.flag,
        }

        if depth > 0:
            data["alt_names"] = self.alt_names

        return data


@dataclass(slots=True)
class Subdivision(DTO):
    id: int
    name: str
    alt_names: list[str]
    type: str
    geonames_code: str | None
    iso_code: str | None
    admin_level: int
    parent: Subdivision | None
    country: Country

    def to_dict(self, depth=1):
        data = {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "geonames_code": self.geonames_code,
            "iso_code": self.iso_code,
            "admin_level": self.admin_level,
        }

        if depth >= 1:
            data["alt_names"] = (self.alt_names,)
            data["parent"] = self.parent.to_dict(depth=0) if self.parent else None
            data["country"] = self.country.to_dict(0)

        return data


@dataclass(slots=True)
class City(DTO):
    id: int
    name: str
    # display_name: str
    admin1: Subdivision
    admin2: Subdivision
    country: Country
    population: int
    lat: float
    lng: float

    def to_dict(self, depth=1):
        return {
            "id": self.id,
            "name": self.name,
            "admin1": self.admin1.to_dict(depth=0) if self.admin1 else None,
            "admin2": self.admin2.to_dict(depth=0) if self.admin2 else None,
            "country": self.country.to_dict(depth=0) if self.country else None,
            "population": self.population,
            "lat": self.lat,
            "lng": self.lng,
        }
