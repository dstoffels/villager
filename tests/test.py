import localis
from rapidfuzz import fuzz

a = localis.countries.get(alpha2="US")
b = localis.countries.get(alpha2="US")

print(a in [b])
