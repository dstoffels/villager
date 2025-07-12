import villager
from rapidfuzz import fuzz
import time

start = time.perf_counter()

res = villager.localities.search("sornas")

duration = time.perf_counter() - start

print([(r.name, s) for r, s in res])
print(f"Duration: {duration:.3f}s")
