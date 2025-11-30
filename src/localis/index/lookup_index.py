from localis.data import Model


class LookupIndex:
    def __init__(self, cache: dict[int, Model], lookup_fields: list[str]):
        self.cache = cache
        self.index: dict[str, dict[str | int, Model]] = {}
        for field in lookup_fields:
            self.index[field] = {}
            for model in cache.values():
                key = getattr(model, field)
                if isinstance(key, str):
                    key = key.lower()
                self.index[field][key] = model

    def get(self, field: str, key: str | int):
        if isinstance(key, str):
            key = key.lower()
        return self.cache.get(key, {})
