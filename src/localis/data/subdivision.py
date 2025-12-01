from dataclasses import dataclass
from .model import DTO, Model, extract_base
from .country import CountryBase, CountryModel


@dataclass(slots=True)
class SubdivisionBase(DTO):
    geonames_code: str | None
    iso_code: str | None
    type: str


@dataclass(slots=True)
class Subdivision(SubdivisionBase):
    aliases: list[str]
    admin_level: int
    parent: SubdivisionBase | None
    country: CountryBase


@dataclass(slots=True)
class SubdivisionModel(Subdivision, Model):
    LOOKUP_FIELDS = ("iso_code", "geonames_code")
    FILTER_FIELDS = {
        "name": ("name", "aliases"),
        "type": ("type",),
        "country": (
            "country.name",
            "country.alpha2",
            "country.alpha3",
            "country.numeric",
        ),
        "admin_level": ("admin_level",),
    }
    SEARCH_FIELDS = {
        "name": 1.0,
        "iso_suffix": 0.5,
        "aliases": 1.0,
        "parent.name": 0.4,
        "country.name": 0.4,
        "country.alpha2": 0.4,
        "country.alpha3": 0.4,
    }

    @property
    def iso_suffix(self) -> str:
        return self.iso_code.split("-")[1] if self.iso_code else ""

    parent: "SubdivisionModel"
    country: CountryModel

    @property
    def dto(self):
        dto: Subdivision = extract_base(self)
        dto.parent = self.parent and extract_base(self.parent, depth=2)
        dto.country = self.country and extract_base(self.country, depth=2)
        return dto

    # @property
    # def search_context(self) -> str:
    #     return " ".join(
    #         [
    #             self.name,
    #             self.iso_suffix,
    #             self.type or "",
    #             self.country.alpha2 if self.country else "",
    #             self.country.alpha3 if self.country else "",
    #             self.country.name if self.country else "",
    #         ],
    #     ).lower()
