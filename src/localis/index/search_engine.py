from localis.data.model import Model
from collections import defaultdict
from rapidfuzz import fuzz
from localis.utils import normalize, generate_trigrams


class SearchEngine:
    def __init__(self, cache: dict[int, Model]):
        self.cache = cache
        self.index: dict[str, set[int]] = defaultdict(set)

        for id, model in cache.items():
            for trigram in model.search_tokens.split("|"):
                self.index[trigram].add(id)

    def search(self, query: str, threshold=0.6, limit=10):
        if not query:
            return []

        self.query = normalize(query)

        candidates = self._get_candidates()

        if not candidates:
            return []

        results = self.score_candidates(candidates)
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]

    def _get_candidates(self) -> set[int]:
        """Intersect token candidates progressively until intersection is empty"""
        candidates = None

        for trigram_candidates in [
            self.index.get(trigram) for trigram in generate_trigrams(self.query)
        ]:
            if not trigram_candidates:
                continue

            if candidates is None:
                candidates = trigram_candidates
            else:
                intersected = candidates & trigram_candidates

                if not intersected or len(intersected) < 700:
                    return candidates

                candidates = intersected

        return candidates

    def _get_token_candidates(self, token: str) -> set[int]:
        """Get all candidates matching this token via trigrams"""
        candidates = self.index.get(token, set())
        if not candidates:
            for trigram in generate_trigrams(token):
                candidates |= self.index.get(trigram, set())

        return candidates

    def score_candidates(self, candidates: set[int]):
        NOISE_THRESHOLD = 0.66

        results = []

        for id in candidates:
            score = 0.0
            matches = 0
            candidate = self.cache[id]

            for field in candidate.search_values:
                field_score = fuzz.token_set_ratio(self.query, field) / 100
                if field_score >= NOISE_THRESHOLD:
                    score += field_score
                    matches += 1

            final_score = score / matches if matches > 0 else 0.0
            if final_score > NOISE_THRESHOLD:
                results.append((candidate.dto, final_score))

        return results

    REMOVE_CHARS = (",", ".")

    def normalize(self, text: str) -> str:
        norm = normalize(text)

        trans_table = str.maketrans("", "", "".join(self.REMOVE_CHARS))
        return norm.translate(trans_table)
