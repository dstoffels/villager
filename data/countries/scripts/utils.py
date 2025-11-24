from dataclasses import dataclass, field
from pathlib import Path


BASE_PATH = Path(__file__).parent.parent


# helper dto class
@dataclass
class CountryDTO:
    name: str
    official_name: str
    alt_names: list[str]
    alpha2: str
    alpha3: str
    numeric: int
    flag: str
    # id: int = field(default=None)

    def dump(self):
        # final dedupe before dump
        self.alt_names = "|".join(set(self.alt_names) - {self.name, self.official_name})
        return [*self.__dict__.values()]
