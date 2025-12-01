from localis.data.model import Model, DTO
from collections import defaultdict
from rapidfuzz import fuzz, process
from localis.utils import normalize, generate_trigrams
import math
import heapq


class SearchEngine:
    def __init__(
        self, cache: dict[int, Model], noise_threshold=0.6, penality_factor=0.15
    ):
        self.cache = cache
        self.NOISE_THRESHOLD = noise_threshold
        self.PENALITY_FACTOR = penality_factor

        self.index: dict[str, set[int]] = defaultdict(set)

        for id, model in cache.items():
            for trigram in model.search_tokens.split("|"):
                self.index[trigram].add(id)

    def search(self, query: str, limit=10):
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
        """Get candidate document IDs matching the query via trigrams"""
        total_docs = len(self.cache)

        # build list of trigrams with their candidate sets and document frequencies
        trigram_list: list[tuple[str, set[int], int]] = []
        for trigram in generate_trigrams(self.query):
            cands = self.index.get(trigram)
            if not cands:
                continue
            df = len(cands)
            trigram_list.append((trigram, cands, df))

        if not trigram_list:
            return set()

        # compute weights for each trigram based on IDF, giving higher weight to rarer trigrams
        trigram_weights: dict[str, float] = {}
        for trigram, _, df in trigram_list:
            trigram_weights[trigram] = math.log(
                (total_docs + 1) / (df + 1)
            )  # IDF weighting

        # aggregate scores for each candidate document
        scores: dict[int, float] = {}
        for trigram, cands, _ in trigram_list:
            weight = trigram_weights[trigram]
            for id in cands:
                scores[id] = scores.get(id, 0.0) + weight

        if not scores:
            return set()

        # select top-k candidates based on aggregated scores
        top_k = max(10, min(total_docs // 50, 500))

        if len(scores) <= top_k:
            return set(scores.keys())

        # get the top_k highest scoring document IDs
        top = heapq.nlargest(top_k, scores.items(), key=lambda x: x[1])
        top_ids = {id for id, _ in top}
        return top_ids

    def score_candidates(self, candidates: set[int]) -> list[tuple[DTO, float]]:

        results = []

        for id in candidates:
            score = 0.0
            match_weights = 0.0
            candidate = self.cache[id]

            for field, weight in candidate.search_values:
                if isinstance(field, list):
                    matches = process.extract(
                        self.query,
                        field,
                        scorer=fuzz.WRatio,
                        score_cutoff=60,
                        limit=None,
                    )
                    field_score = (
                        max(score for _, score, _ in matches) / 100.0
                        if matches
                        else 0.0
                    )
                else:
                    field_score = fuzz.WRatio(self.query, field) / 100.0

                # Only consider significant matches
                if field_score >= self.NOISE_THRESHOLD:
                    score += field_score * weight
                    match_weights += weight
                else:
                    # small penalty for non-matching fields for tie breaking
                    penalty = (
                        (self.NOISE_THRESHOLD - field_score)
                        * self.PENALITY_FACTOR
                        * weight
                    )
                    score -= penalty

            final_score = score / match_weights if match_weights > 0 else 0.0
            if final_score > self.NOISE_THRESHOLD:
                results.append((candidate.dto, final_score))

        return results

    REMOVE_CHARS = (",", ".")

    def normalize(self, text: str) -> str:
        norm = normalize(text)

        trans_table = str.maketrans("", "", "".join(self.REMOVE_CHARS))
        return norm.translate(trans_table)
