from dataclasses import dataclass
from .model import DTO, Model


@dataclass(slots=True)
class CountryBase(DTO):
    alpha2: str
    alpha3: str


@dataclass(slots=True)
class Country(CountryBase):
    official_name: str
    aliases: list[str]
    numeric: str
    flag: str


@dataclass(slots=True)
class CountryModel(Country, Model):
    SEARCH_FIELDS = {
        "name": 1.0,
        "official_name": 1.0,
        "alpha2": 1.0,
        "alpha3": 1.0,
        "aliases": 1.0,
    }
    LOOKUP_FIELDS = ("alpha2", "alpha3", "numeric")
    FILTER_FIELDS = {"name": ("name", "official_name", "aliases")}

    def set_search_meta(self):
        self.search_values = (
            self.name.lower(),
            self.official_name.lower(),
            self.alpha2.lower(),
            self.alpha3.lower(),
            *(a.lower() for a in self.aliases),
        )

        self.search_context = " ".join(self.search_values)
