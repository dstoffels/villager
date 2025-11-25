from localis.data.model import Model
from collections import defaultdict


class TrigramEngine:
    def __init__(self, cache: dict[int, Model]):
        index: dict[str, set[int]] = defaultdict(set)
        trigram_counts: dict[int, int] = {}

        for id, model in cache.items():
            name = model.name.lower()
            # for name in model.search_docs:
            trigram_cnt = max(len(name) - 2, 1)
            trigram_counts[id] = trigram_cnt

            if trigram_cnt == 1:
                index[name].add(id)
                continue

            for i in range(trigram_cnt):
                trigram = name[i : i + 3]
                index[trigram].add(id)

        self.index = index
        self.doc_trigram_counts = trigram_counts

    def search(self, query: str, threshold=0.6) -> list[tuple[int, float]]:
        query = query.lower().replace(",", "").replace(".", "").replace("St.", "Saint")

        # early exit for shorties
        if len(query) < 4:
            exact_matches = self.index.get(query, set())
            return {(id, 1.0) for id in exact_matches}

        query_trigram_cnt = len(query) - 2

        # count ngram hits for each candidate
        hit_counts: dict[int, int] = defaultdict(int)

        for i in range(len(query) - 2):
            trigram = query[i : i + 3]
            weight = 2 if i == 0 else 1

            # grab candidates for ngram
            for id in self.index.get(trigram, ()):
                hit_counts[id] += weight

        # DTO.id, score
        candidates: list[tuple[int, float]] = []

        for id, hits in hit_counts.items():
            candidate_trigram_cnt = self.doc_trigram_counts[id]

            max_hits = min(query_trigram_cnt, candidate_trigram_cnt) + 1
            score = hits / max_hits
            if score >= threshold:
                candidates.append((id, score))

        # descending score sorting
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates
