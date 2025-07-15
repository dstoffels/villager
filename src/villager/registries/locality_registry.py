from villager.registries.registry import Registry
from villager.db import LocalityModel, SubdivisionModel, CountryModel, Locality
from villager.utils import normalize
from villager.literals import CountryCode, CountryName


class LocalityRegistry(Registry[LocalityModel, Locality]):
    """Registry for localities containing"""

    def __init__(self, model_cls):
        super().__init__(model_cls)
        self._order_by = ", population DESC"

    osm_type_map = {
        "way": "w",
        "node": "n",
        "relation": "r",
    }

    def get(self, identifier: str) -> Locality:
        '''Fetch a locality by exact OSM type & id. Required format: "[type]:[id]"'''
        if not identifier:
            return None

        type, id = identifier.strip().split(":")

        type = self.osm_type_map.get(type.lower(), type)

        row = self._model_cls.get(
            (LocalityModel.osm_id == id) & (LocalityModel.osm_type == type)
        )
        return row.dto

    def lookup(
        self,
        name: str,
        country: CountryCode | CountryName = None,
        subdivision: str = None,
        **kwargs,
    ) -> list[Locality]:
        """Lookup localities by exact name, optionally filtered by country and/or subdivision."""
        if not name:
            return []

        norm_q = normalize(name)
        if country:
            norm_q += f" {country}"
        if subdivision:
            norm_q += f" {subdivision}"

        rows = self._model_cls.fts_match(norm_q, exact=True)
        return [r.dto for r in rows]

    def _sort_matches(
        self, matches: list[tuple[Locality, float]], limit: int
    ) -> list[Locality]:
        return [
            dto
            for dto, score in sorted(
                matches, key=lambda r: (r[1], r[0].population or 0), reverse=True
            )[:limit]
        ]
