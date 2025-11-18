from villager.search.search_base import SearchBase
from rapidfuzz import fuzz
from villager.utils import normalize


class FuzzySearch(SearchBase):
    NOISE_THRESHOLD = 0.6

    def score_candidate(self, candidate):
        score = 0.0
        total_matched_weight = 0.0

        for field, weight in self.field_weights.items():
            value = getattr(candidate, field, "")
            if value:
                if "|" in value:
                    field_score = fuzz.partial_token_sort_ratio(value, self.query) / 100
                else:
                    field_score = fuzz.token_set_ratio(value, self.query) / 100

                # # Filter noise
                if field_score >= self.NOISE_THRESHOLD:
                    score += field_score * weight
                    total_matched_weight += weight
        return score / total_matched_weight if total_matched_weight > 0 else 0.0
