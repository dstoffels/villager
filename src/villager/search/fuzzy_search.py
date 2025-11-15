# from villager.db import Model
# from villager.utils import normalize
# from villager.dtos import DTO


# class Search:
#     MAX_ITERATIONS = 20
#     MIN_TOKEN_LEN = 3
#     NGRAM_LEN = 2

#     def __init__(
#         self,
#         query: str,
#         model_cls: type[Model],
#         field_weights: dict[str, float],
#         limit: int = None,
#     ):
#         self.query: str = normalize(query)
#         self.model_cls: type[Model] = model_cls
#         self.field_weights: dict[str, float] = field_weights
#         self.limit: int | None = limit

#         # split query into tokens and ngram each one
#         self.q_token_ngrams: list[set[str]] = [
#             self._ngram(t, self.NGRAM_LEN) for t in self.query.split(" ")
#         ]

#         # hold a map of seen candidates to prevent repeated scoring
#         self._seen: dict[int, Model]
#         self._strong_matches = dict[int, Model]
#         self._weak_matches = dict[int, Model]
#         self._iteration = 0

#         self.main()

#     @property
#     def results(self) -> list[DTO, float]:
#         return []

#     def main(self):
#         # run loop until no new, acceptable fuzzy matches are produced from fts candidates?

#         for i in enumerate(20):

#             self._score()
#             pass

#     def _fetch_candidates(self, tokens: list[str]) -> list[Model]:

#         pass

#     def _score(self, model: Model) -> float:
#         score = 0.0

#         for q_token_ngram in self.q_token_ngrams:
#             for field, weight in self.field_weights.items():
#                 value = getattr(model, field, "")
#                 for token in value.replace("|", " ").split():
#                     score += self._score_ngrams(q_token_ngram, token) * weight
#         return score

#     def _score_ngrams(self, q_token_ngram: set[str], token: str) -> float:
#         token_ngrams = self._ngram(token)

#         if not q_token_ngram or not token_ngrams:
#             return 0.0
#         return len(q_token_ngram & token_ngrams) / len(q_token_ngram | token_ngrams)

#     def _ngram(self, s: str, n: int = 2) -> set[str]:
#         s = s.lower().replace(" ", "")
#         return {s[i : i + n] for i in range(len(s) - n + 1)}

#     def _truncate_tokens(self, tokens: list[str]) -> list[str]:
#         return [t[:-1] for t in tokens if len(t) > self.MIN_TOKEN_LEN]


# # def search_old(self, query: str, limit=5, **kwargs) -> list[TDTO]:
# #     """"""
# #     if not query:
# #         return []

# #     norm_query = normalize(query)
# #     tokens = norm_query.split()
# #     min_len = len(tokens) if len(tokens) > 1 else 2
# #     total_tok_len = sum(len(t) for t in tokens)

# #     MAX_ITERATIONS = 20
# #     NAME_WEIGHT = 0.7
# #     TOKEN_WEIGHT = 0.3

# #     matches: dict[int, tuple[TDTO, float]] = {}

# #     # exact match on initial query unless overridden
# #     candidates: list[RowData[TDTO]] = self._model_cls.fts_match(
# #         norm_query, exact_match=True, order_by=self._order_by
# #     )

# #     for step in range(MAX_ITERATIONS):
# #         results = process.extract(
# #             norm_query,
# #             choices=[c.search_tokens for c in candidates],
# #             scorer=fuzz.WRatio,
# #             limit=None,
# #         )

# #         for _, token_score, idx in results:
# #             candidate = candidates[idx]
# #             name_score = fuzz.ratio(norm_query, candidate.dto.name)

# #             # consider additional attributes for scoring. uses name weighting on the highest score found betwen name and additional attrs
# #             for attr in self._addl_search_attrs:
# #                 attr_value = getattr(candidate.dto, attr, None)
# #                 if attr_value:
# #                     attr_score = fuzz.ratio(norm_query, normalize(attr_value))
# #                     if attr_score > name_score:
# #                         name_score = attr_score

# #             score = name_score * NAME_WEIGHT + token_score * TOKEN_WEIGHT

# #             matches[candidate.id] = (candidate, score)

# #         # stop if we have enough matches or tokens are too short
# #         if len(matches) >= limit * 2 or total_tok_len <= min_len:
# #             break

# #         # truncate tokens and generate next FTS query
# #         new_tokens = []
# #         total_tok_len = 0
# #         for t in tokens:
# #             new_len = max(2, len(t) - step)
# #             new_tokens.append(t[:new_len])
# #             total_tok_len += new_len
# #         fts_q = " ".join(new_tokens)

# #         candidates = self._model_cls.fts_match(fts_q, order_by=self._order_by)

# #     return self._sort_matches(matches.values(), limit)
