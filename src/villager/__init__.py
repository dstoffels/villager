from villager.registries import CountryRegistry, SubdivisionRegistry, LocalityRegistry
from villager.db import CountryModel, SubdivisionModel, LocalityModel
from villager.db.dtos import Country, Subdivision, Locality

countries = CountryRegistry(CountryModel)
subdivisions = SubdivisionRegistry(SubdivisionModel)
localities = LocalityRegistry(LocalityModel)
