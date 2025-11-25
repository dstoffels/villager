from dataclasses import dataclass
from .model import DTO, Model
from sys import intern


@dataclass(slots=True)
class CountryBase(DTO):
    alpha2: str
    alpha3: str


@dataclass(slots=True)
class Country(CountryBase):
    official_name: str
    alt_names: list[str]
    numeric: int
    flag: str


@dataclass(slots=True)
class CountryModel(Country, Model):

    def parse_docs(self):
        self.search_docs = (
            intern(self.name.lower()),
            intern(self.alpha2.lower()),
            intern(self.alpha3.lower()),
            intern(self.official_name.lower()),
            *(intern(alt.lower()) for alt in self.alt_names),
        )
