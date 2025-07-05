from .registry import Registry
from ..db import LocalityModel, SubdivisionModel, CountryModel
from ..types import Locality
from peewee import prefetch
from peewee import fn


class LocalityRegistry(Registry[LocalityModel, Locality]):
    """Registry for localities.

    WARNING: using this registry as an iterable will load all localities into memory. This is very heavy and slow, iterate at your own risk!

    Alternatively, get_batch allows you to load a filtered slice of the locality table by name prefix.
    """

    def __init__(self, db, model):
        super().__init__(db, model)

    def get(self, identifier: int) -> Locality:
        if isinstance(identifier, str):
            try:
                identifier = int(identifier)
            except:
                return None
        return self._model.get_or_none(LocalityModel.osm_id == identifier)

    def lookup(self, identifier):
        return super().lookup(identifier)

    def search(self, query, limit=5):
        return super().search(query, limit)

    def get_batch(
        self, limit=1000, offset=0, name_prefix: str | None = None
    ) -> list[Locality]:
        """Loads a batch of localities from the database."""
        q = self._model.select()

        if name_prefix:
            q = q.where(self._model.name.startswith(name_prefix))

        q = q.limit(limit).offset(offset)
        prefetched = prefetch(q, SubdivisionModel.select(), CountryModel.select())
        return [m.to_dto() for m in prefetched]

    def _load_cache(self) -> list[Locality]:
        q = self._model.select()
        results = []
        for model in self._batched_prefetch(q):
            results.append(model.to_dto())
        return results

    def _batched_prefetch(self, query, batch_size=1000):
        """Yields LocalityModel instances in batches, using prefetch()."""
        progress = 0
        offset = 0
        while True:
            # Select is lazily evaluated — pass the query directly to prefetch
            current_progress = int(offset / self.count * 100)
            if current_progress > progress:
                progress = current_progress
                print(f"Loading localities... {progress}%")
            batch_query = query.limit(batch_size).offset(offset)
            prefetched = list(
                prefetch(batch_query, SubdivisionModel.select(), CountryModel.select())
            )
            if not prefetched:
                break
            yield from prefetched
            offset += batch_size
