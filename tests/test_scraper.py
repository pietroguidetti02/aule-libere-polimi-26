from search.polimi_scraper import PolimiAuleScraper
from datetime import datetime

scraper = PolimiAuleScraper()

# Test 1: Ricerca base
print("=== TEST 1: Tutte le sedi, oggi ===")
risultati = scraper.search_aule_libere()
print(f"Aule trovate: {risultati['totale']}")
print(f"Aule studio: {len(risultati['aule_studio'])}")
print(f"Aule normali: {len(risultati['aule_normali'])}")

# Test 2: Sede specifica
print("\n=== TEST 2: Milano Città Studi ===")
risultati = scraper.search_aule_libere(sede="MIA")
print(f"Aule trovate: {risultati['totale']}")

# Test 3: Orario specifico
print("\n=== TEST 3: Orario 15:15-17:15 ===")
risultati = scraper.search_aule_libere(
    ora_dal="15:15",
    ora_al="17:15"
)
print(f"Aule trovate: {risultati['totale']}")

# Mostra prime 3 aule
if risultati['aule_normali']:
    print("\nPrime 3 aule:")
    for aula in risultati['aule_normali'][:3]:
        print(f"  - {aula['sigla']}: {aula['dove']}")
