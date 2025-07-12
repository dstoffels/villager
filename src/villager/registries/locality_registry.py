from villager.registries.registry import Registry
from villager.db import LocalityModel, SubdivisionModel, CountryModel, Locality
from villager.utils import normalize
from villager.literals import CountryCode


class LocalityRegistry(Registry[LocalityModel, Locality]):
    """Registry for localities."""

    osm_type_map = {
        "way": "w",
        "node": "n",
        "relation": "r",
    }

    def get(self, identifier: str) -> Locality:
        '''Fetch a locality by exact OSM type & id. Format: "[osm_type]:[osm_id]"'''
        if not identifier:
            return None

        type, id = identifier.strip().split(":")

        type = self.osm_type_map.get(type.lower(), type)

        row = self._model_cls.get(
            (LocalityModel.osm_id == id) & (LocalityModel.osm_type == type)
        )
        return row.dto

    def lookup(self, name: str, **kwargs) -> list[Locality]:
        """Lookup localities by exact name."""
        if not name:
            return []

        name = normalize(name)

        rows = self._model_cls.select(LocalityModel.normalized_name == name)
        return [r.dto for r in rows]

    def search(
        self, query, subdivision: str = "", country: CountryCode = "", limit=5, **kwargs
    ) -> list[tuple[Locality, float]]:
        """Fuzzy search localities, optionally filtered by country code or subdivision iso_code."""

        if not query:
            return []

        query = normalize(query)

        # reset
        self._use_fts_match = True

        if subdivision:
            self._use_fts_match = False
            self._search_candidates = self._model_cls.where(
                f'sub1_iso_code = "{subdivision}"'
            )
        elif country:
            self._use_fts_match = False
            self._search_candidates = self._model_cls.where(
                f'country_alpha2 = "{country}"'
            )
        else:
            self._search_candidates = self._model_cls.fts_match(query, exact=True)

        return self._fuzzy_search(query, limit)
