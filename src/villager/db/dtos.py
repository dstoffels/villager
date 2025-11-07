from dataclasses import dataclass, asdict, field
import json
from abc import ABC, abstractmethod


@dataclass
class DTO(ABC):
    id: int
    name: str

    def to_dict(self):
        return asdict(self)

    def json(self):
        return json.dumps(self.to_dict())


@dataclass
class Country(DTO):
    id: int
    name: str
    official_name: str
    alpha2: str
    alpha3: str
    numeric: int
    aliases: list[str] = field(default_factory=list)
    flag: str = ""


@dataclass
class SubdivisionBasic:
    name: str
    code: str
    admin_level: int


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
    aliases: list[str]
    country: str
    country_alpha2: str
    country_alpha3: str
    subdivisions: list[SubdivisionBasic]

    # @property
    # def search_tokens(self) -> str:
    #     return f"{self.name} {self.code} {self.country} {self.country_alpha2} {self.country_alpha3}"


@dataclass
class City(DTO):
    id: int
    name: str
    display_name: str | None
    population: int | None
    lat: float
    lng: float
    country: str
    country_alpha2: str
    country_alpha3: str
    subdivisions: list[SubdivisionBasic]

    # @property
    # def search_tokens(self):
    #     return f'{self.name} {" ".join([f'{s.name} {s.code}' for s in self.subdivisions])} {self.country} {self.country_alpha2} {self.country_alpha3}'
