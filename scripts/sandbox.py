import villager
from rapidfuzz import process, fuzz
import time


dtos = villager.localities

while True:
    query = input("Search: ")
    if not query:
        break
    start = time.perf_counter()
    results = villager.localities.search(query)
    duration = time.perf_counter() - start
    results = [f"{r.display_name}" for r in results]
    print(results)
    print(f"Duration: {duration:.3f}s")


# duration = 0.0
# for c in dtos:
#     start = time.perf_counter()
#     results = villager.localities.search(c.name)
#     results = [r.name for r in results]
#     duration += time.perf_counter() - start

# print(f"Duration: {duration:.3f}s")
f = [
    "san francisco heredia costa rica cr cri",
    "san francisco keson philippines ph phl",
    "san francisco cebu philippines ph phl",
    "san francisco cordoba argentina ar arg",
    "san francisco bulacan philippines ph phl",
    "san francisco peten guatemala gt gtm",
    "san francisco la guajira colombia co col",
    "san francisco cochabamba bolivia bo bol",
    "san francisco el beni bolivia bo bol",
    "san francisco chiriqui panama pa pan",
    "san francisco alto cochabamba bolivia bo bol",
    "san francisco jujuy argentina ar arg",
    "san francisco tabasco mexico mx mex",
    "san francisco granma cuba cu cub",
    "san francisco santa cruz bolivia bo bol",
    "puerto san francisco cochabamba bolivia bo bol",
    "san francisco moyejon peten guatemala gt gtm",
    "san francisco jalisco mexico mx mex",
    "san francisco san martin peru pe per",
    "san francisco putumayo colombia co col",
    "san francisco cundinamarca colombia co col",
    "san francisco antioquia colombia co col",
    "san francisco narino colombia co col",
    "san francisco meta colombia co col",
    "san francisco choco colombia co col",
    "san francisco sucre colombia co col",
    "san francisco guayas ecuador ec ecu",
    "san francisco tungurahua ecuador ec ecu",
    "san francisco sucumbios ecuador ec ecu",
    "san francisco esmeraldas ecuador ec ecu",
    "san francisco quiche guatemala gt gtm",
    "san francisco izabal guatemala gt gtm",
    "san francisco tombali guineabissau gw gnb",
    "san francisco lempira honduras hn hnd",
    "san francisco atlantida honduras hn hnd",
    "san francisco nayarit mexico mx mex",
    "san francisco chiapas mexico mx mex",
    "san francisco guerrero mexico mx mex",
    "san francisco mexico mexico mx mex",
    "san francisco queretaro mexico mx mex",
    "san francisco hidalgo mexico mx mex",
    "san francisco sinaloa mexico mx mex",
    "san francisco sonora mexico mx mex",
    "san francisco durango mexico mx mex",
    "san francisco tamaulipas mexico mx mex",
    "san francisco yucatan mexico mx mex",
    "san francisco esteli nicaragua ni nic",
    "san francisco matagalpa nicaragua ni nic",
    "san francisco boaco nicaragua ni nic",
    "san francisco veraguas panama pa pan",
    "san francisco ayacucho peru pe per",
    "san francisco arequipa peru pe per",
    "san francisco ica peru pe per",
    "san francisco lima peru pe per",
    "san francisco hunin peru pe per",
    "san francisco moquegua peru pe per",
    "san francisco puno peru pe per",
    "san francisco cusco peru pe per",
    "san francisco piura peru pe per",
    "san francisco ancash peru pe per",
    "san francisco pasco peru pe per",
    "san francisco cajamarca peru pe per",
    "san francisco loreto peru pe per",
    "san francisco antike philippines ph phl",
    "san francisco iloilo philippines ph phl",
    "san francisco bukidnon philippines ph phl",
    "san francisco bohol philippines ph phl",
    "san francisco leyte philippines ph phl",
    "san francisco batangas philippines ph phl",
    "san francisco albay philippines ph phl",
    "san francisco pampanga philippines ph phl",
    "san francisco tarlac philippines ph phl",
    "san francisco laguna philippines ph phl",
    "san francisco kirino philippines ph phl",
    "san francisco isabela philippines ph phl",
    "san francisco samar philippines ph phl",
    "san francisco sorsogon philippines ph phl",
    "san francisco caazapa paraguay py pry",
    "san francisco canelones uruguay uy ury",
    "san francisco zulia venezuela ve ven",
    "san francisco bolivar venezuela ve ven",
    "san francisco monagas venezuela ve ven",
    "san francisco lara venezuela ve ven",
    "san francisco falcon venezuela ve ven",
    "san francisco merida venezuela ve ven",
    "san francisco anzoategui venezuela ve ven",
    "san francisco aragua venezuela ve ven",
    "san francisco san jose costa rica cr cri",
    "san francisco san luis potosi mexico mx mex",
    "villa de san francisco francisco morazan honduras hn hnd",
    "san francisco del ocote francisco morazan honduras hn hnd",
    "caserio san francisco amazonas colombia co col",
    "vereda san francisco cauca colombia co col",
    "san francisco el oro ecuador ec ecu",
    "san francisco cununguachay chimborazo ecuador ec ecu",
    "san francisco 2 sucumbios ecuador ec ecu",
    "puerto san francisco sucumbios ecuador ec ecu",
    "san francisco zapotitlan suchitepequez guatemala gt gtm",
    "san francisco santa barbara honduras hn hnd",
    "san francisco ixhuatan oaxaca mexico mx mex",
]
