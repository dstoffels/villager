from collections import defaultdict
from typing import Generic, TypeVar
from localis.data import DTO

TDTO = TypeVar("TDTO", bound=DTO)


class NgramIndex(Generic[TDTO]):
    """Ngram search engine using trigram as default."""

    def __init__(self, n: int = 3):
        self.n = n
        self.index: dict[str, set[TDTO]] = defaultdict(set)

    def add(self, text: str, id: int):
        """Add bigrams to index"""

        # normalize
        text = text.lower()

        # store shorties directly
        if len(text) < self.n:
            self.index[text].add(id)
            return

        # build and index ngrams
        for i in range(len(text) - self.n + 1):
            ngram = text[i : i + self.n]
            self.index[ngram].add(id)

    def search(self, query: str, threshold=0.2) -> list[tuple[int, float]]:
        query = query.lower()

        # early exit for shorties
        if len(query) < self.n:
            exact_matches = self.index.get(query, set())
            return {id: 1.0 for id in exact_matches}

        query_ngram_cnt = len(query) - self.n + 1

        # count ngram hits for each candidate
        hit_counts: dict[int, int] = defaultdict(int)

        for i in range(len(query) - self.n + 1):
            ngram = query[i : i + self.n]

            # grab candidates for ngram
            for candidate_id in self.index.get(ngram, set()):
                hit_counts[candidate_id] += 1

        # DTO.id, score
        candidates: list[tuple[int, float]] = []

        for id, hits in hit_counts.items():
            score = hits / query_ngram_cnt
            if score >= threshold:
                candidates.append((id, score))

        # descending score sorting
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates
