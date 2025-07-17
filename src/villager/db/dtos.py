from dataclasses import dataclass, asdict, field
import json
from abc import ABC, abstractmethod


@dataclass
class DTO(ABC):
    def to_dict(self):
        return asdict(self)

    def json(self):
        return json.dumps(self.to_dict())

    # def __str__(self):
    #     return self.json()


@dataclass
class Country(DTO):
    id: int
    name: str
    alpha2: str
    alpha3: str
    long_name: str

    @property
    def search_tokens(self):
        return f"{self.name} {self.alpha2} {self.alpha3} {self.long_name}"


@dataclass
class Subdivision(DTO):
    """A country subdivision such as a state, province, or territory."""

    id: int
    name: str
    iso_code: str
    code: str
    category: str
    parent_iso_code: str
    admin_level: int
    alt_name: str
    country: str
    country_alpha2: str
    country_alpha3: str


@dataclass
class SubdivisionBasic(DTO):
    name: str
    code: str
    admin_level: int


@dataclass
class Locality(DTO):
    """A geographic locality such as a city, town, village, or hamlet."""

    id: int
    name: str
    display_name: str | None
    type: str | None
    population: int | None
    lat: float
    lng: float
    country: str
    country_alpha2: str
    country_alpha3: str
    subdivisions: list[SubdivisionBasic]
