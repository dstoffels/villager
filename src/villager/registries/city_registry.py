from villager.registries.registry import Registry
from villager.db import CityModel, City, MetaStore
import requests
import io


class CityRegistry(Registry[CityModel, City]):
    """Registry for cities"""

    SEARCH_FIELD_WEIGHTS = {
        "name": 1.0,
        "alt_names": 1.0,
        "admin1": 0.3,
        "admin2": 0.1,
        "country": 0.2,
    }

    META_LOADED_KEY = "cities_loaded"
    META_URL_KEY = "cities_tsv_url"

    def __init__(self, model_cls):
        super().__init__(model_cls)
        self._order_by = "population DESC"

        self._meta = MetaStore()
        self._loaded = self._read_loaded_flag()

    @property
    def search_field_weights(self):
        pass

    def _read_loaded_flag(self) -> bool:
        return self._meta.get(self.META_LOADED_KEY) == "1"

    def load(self) -> None:
        if self._loaded:
            print("Cities already loaded.")
            return

        print("Loading Cities...")
        url = self._meta.get(self.META_URL_KEY)
        if url:
            print("Downloading TSV fixture...")

            response = requests.get(url)
            response.raise_for_status()

            print("TSV fixture downloaded, loading into database...")
            tsv = io.StringIO(response.text)
            CityModel.load(tsv)

            self._meta.set(self.META_LOADED_KEY, "1")
            self._loaded = self._read_loaded_flag()
            print(f"{self.count} cities loaded.")

        else:
            print("No download url availale for cities dataset")
            print(
                "Check for the latest cities.tsv at https://github.com/dstoffels/villager"
            )

    def unload(self) -> None:
        if not self._loaded:
            print("No cities to unload.")
        else:
            print(f"Removing {self.count} cities")
            CityModel.drop()
            self._meta.set(self.META_LOADED_KEY, "0")
            self._loaded = self._read_loaded_flag()
            self._count = None

            print("Cities unloaded from db.")

    @property
    def count(self):
        self._ensure_loaded()
        return super().count

    def _ensure_loaded(self):
        if not self._loaded:
            raise RuntimeError(
                "Cities data not yet loaded. Load with `villager.cities.load()` or `villager load cities` from the CLI."
            )

    def get(self, *, id: int = None, geonames_id: str = None, **kwargs):
        self._ensure_loaded()
        cls = self._model_cls

        field_map = {
            "id": None,
            "geonames_id": cls.geonames_id,
        }

        model = None
        for arg, field in field_map.items():
            val = locals()[arg]
            if val is not None:
                model = cls.get_by_id(val) if arg == "id" else cls.get(field == val)

        return model.to_dto() if model is not None else None

    def filter(
        self,
        query: str = None,
        name: str = None,
        limit: int = None,
        admin1: str = None,
        admin2: str = None,
        country: str = None,
        alt_name: str = None,
        **kwargs,
    ):
        self._ensure_loaded()
        if kwargs:
            return []
        if admin1:
            kwargs["admin1"] = admin1
        if admin2:
            kwargs["admin2"] = admin2
        if country:
            kwargs["country"] = country
        if alt_name:
            kwargs["alt_names"] = alt_name

        return super().filter(query, name, limit, **kwargs)

    def search(self, query, limit=None, **kwargs):
        self._ensure_loaded()
        return super().search(query, limit, **kwargs)
