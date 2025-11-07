from dataclasses import dataclass, field


@dataclass
class SubdivisionDTO:
    name: str
    country_alpha2: str
    country_alpha3: str
    country_name: str
    geonames_id: str
    geonames_code: str
    parent_geonames_code: str
    names: list[str] = field(default_factory=list)
    category: str = ""
    iso_code: str = ""
