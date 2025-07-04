# from ..scripts.parser import load_countries, load_subdivisions, load_localities
# from .types import Country, Subdivision
# from dataclasses import replace
# from collections import defaultdict


# def build_data() -> tuple[list[Country], list[Subdivision]]:
#     countries = load_countries()
#     countries_by_alpha2 = {c.alpha2: c for c in countries}
#     subdivisions = load_subdivisions(countries_by_alpha2)
#     localities = load_localities(subdivisions)

#     print(len(localities))

#     return countries, subdivisions
