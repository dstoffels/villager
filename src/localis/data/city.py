from dataclasses import dataclass
from .model import DTO, Model, extract_base
from .country import CountryBase, CountryModel
from .subdivision import SubdivisionBase, SubdivisionModel
from sys import intern


@dataclass(slots=True)
class City(DTO):
    # display_name: str
    ascii_name: str
    admin1: SubdivisionBase
    admin2: SubdivisionBase
    country: CountryBase
    population: int
    lat: float
    lng: float


@dataclass(slots=True)
class CityModel(City, Model):
    admin1: SubdivisionModel
    admin2: SubdivisionModel
    country: CountryModel

    @property
    def dto(self) -> City:
        dto: City = extract_base(self, depth=1)
        dto.admin1 = self.admin1 and extract_base(self.admin1, depth=2)
        dto.admin2 = self.admin2 and extract_base(self.admin2, depth=2)
        dto.country = self.country and extract_base(self.country, depth=2)
        return dto

    def parse_docs(self):
        self.name_str = intern(self.name.lower())
