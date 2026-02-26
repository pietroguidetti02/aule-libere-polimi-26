import requests
import json
import os
from bs4 import BeautifulSoup
from datetime import datetime


class PolimiAuleScraper:
    """
    Scraper per il nuovo sistema aule libere PoliMi
    """
    
    def __init__(self):
        self.base_url = "https://onlineservices.polimi.it/spazi/spazi/controller/RicercaAuleLibere.do"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.sedi = {
            'tutte': 'Tutte',
            'COE': 'Como',
            'CRG': 'Cremona',
            'GEM': 'Genova',
            'LCF': 'Lecco',
            'MNI': 'Mantova',
            'MIB': 'Milano Bovisa',
            'MIA': 'Milano Città Studi',
            'MIF': 'Milano Tortona',
            'PCL': 'Piacenza',
            'MIC': 'Servizi',
            'MID': 'Sesto Ulteriano'
        }
        
        # Carica aule con prese
        try:
            json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'json', 'roomsWithPower.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                self.rooms_with_power = set(json.load(f))
        except Exception as e:
            print(f"Errore caricamento roomsWithPower.json: {e}")
            self.rooms_with_power = set()

    
    def search_aule_libere(self, sede="tutte", giorno=None, ora_dal="08:15", ora_al="10:15"):
        """
        Cerca aule libere al PoliMi
        
        Args:
            sede: str - Codice sede (es: "MIA", "MIB", "tutte")
            giorno: datetime - Data da cercare (default: oggi)
            ora_dal: str - Orario inizio formato HH:MM
            ora_al: str - Orario fine formato HH:MM
        
        Returns:
            dict - {
                'aule_studio': [...],
                'aule_normali': [...],
                'totale': int,
                'sede_nome': str,
                'data': str,
                'orario': str
            }
        """
        if giorno is None:
            giorno = datetime.now()
        
        # Parametri richiesta POST
        # Gestione case-sensitivity: "tutte" minuscolo, altri codici (es. MIA) maiuscoli
        sede_param = "tutte" if sede.lower() == "tutte" else sede.upper()
        
        params = {
            'jaf_currentWFID': 'main',
            'spazi___model___formbean___RicercaAuleLibereVO___postBack': 'true',
            'spazi___model___formbean___RicercaAuleLibereVO___formMode': 'FILTER',
            'spazi___model___formbean___RicercaAuleLibereVO___sede': sede_param,
            'spazi___model___formbean___RicercaAuleLibereVO___giorno_day': str(giorno.day),
            'spazi___model___formbean___RicercaAuleLibereVO___giorno_month': str(giorno.month),
            'spazi___model___formbean___RicercaAuleLibereVO___giorno_year': str(giorno.year),
            'jaf_spazi___model___formbean___RicercaAuleLibereVO___giorno_date_format': 'dd/MM/yyyy',
            'spazi___model___formbean___RicercaAuleLibereVO___orario_dal': ora_dal,
            'spazi___model___formbean___RicercaAuleLibereVO___orario_al': ora_al,
            'evn_ricerca': 'Ricerca aule libere'
        }
        
        try:
            response = self.session.post(self.base_url, data=params, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            aule_studio = self._parse_tabella(soup, 'aulestudiocoll')
            aule_normali = self._parse_tabella(soup, 'aule')
            
            tot_studio = sum(len(v) for v in aule_studio.values())
            tot_normali = sum(len(v) for v in aule_normali.values())
            
            return {
                'aule_studio': aule_studio,
                'aule_normali': aule_normali,
                'totale': tot_studio + tot_normali,
                'sede_nome': self.sedi.get(sede.upper(), 'Tutte'),
                'data': giorno.strftime('%d/%m/%Y'),
                'orario': f"{ora_dal} - {ora_al}",
                'ora_al': ora_al
            }
            
        except requests.RequestException as e:
            print(f"Errore richiesta: {e}")
            return {
                'aule_studio': [],
                'aule_normali': [],
                'totale': 0,
                'sede_nome': self.sedi.get(sede.upper(), 'Tutte'),
                'data': giorno.strftime('%d/%m/%Y'),
                'orario': f"{ora_dal} - {ora_al}",
                'errore': str(e)
            }
    
    def _parse_tabella(self, soup, table_id):
        """
        Estrae aule da una tabella specifica e le raggruppa per edificio
        
        Args:
            soup: BeautifulSoup object
            table_id: str - 'aulestudiocoll' o 'aule'
        
        Returns:
            dict - Dizionario con {edificio: [lista_aule]}
        """
        edifici = {}
        
        # Trova la tabella con id specifico
        tabella = soup.find('table', id=table_id)
        if not tabella:
            return edifici
        
        tbody = tabella.find('tbody', class_='TableDati-tbody')
        if not tbody:
            return edifici
        
        righe = tbody.find_all('tr')
        
        for riga in righe:
            celle = riga.find_all('td')
            if len(celle) >= 6:
                # Colonna 1: Dove (edificio + indirizzo)
                dove_text = celle[0].get_text(separator=' ', strip=True)
                
                # Colonna 2: Sigla (nome aula in <strong>)
                sigla_tag = celle[1].find('strong')
                sigla = sigla_tag.text.strip() if sigla_tag else celle[1].text.strip()
                
                # Estrazione edificio
                edificio = "Altro"
                if '.' in sigla:
                    parts = sigla.split('.')
                    if parts[0].isdigit():
                        edificio = f"Edificio {parts[0]}"
                elif ' ' in sigla:
                    parts = sigla.split(' ')
                    if parts[0].isdigit():
                        edificio = f"Edificio {parts[0]}"
                
                if edificio == "Altro":
                    # Tenta da 'dove_text' (es. "Via Bonardi" -> Edificio 11?)
                    # Spesso PoliMi ha mapping fissi. Per ora usiamo l'indirizzo se non troviamo numero
                    indirizzo = dove_text.split(',')[-1].strip()
                    edificio = indirizzo

                # Estrazione ID aula dal link (colonna 3 - indice 2)
                has_power = False
                try:
                    link_tag = celle[2].find('a')
                    if link_tag and 'href' in link_tag.attrs:
                        href = link_tag['href']
                        # Cerca parametro idaula nell'URL
                        # Esempio: ...&idaula=1234&...
                        if 'idaula=' in href:
                            id_aula_str = href.split('idaula=')[1].split('&')[0]
                            if int(id_aula_str) in self.rooms_with_power:
                                has_power = True
                except Exception as e:
                    # In caso di errore nel parsing link, assume no power
                    pass

                # Colonne 4, 5, 6: Categoria, Tipologia, Dipartimento
                aula = {
                    'sigla': sigla,
                    'dove': dove_text,
                    'categoria': celle[3].text.strip(),
                    'tipologia': celle[4].text.strip(),
                    'dipartimento': celle[5].text.strip(),
                    'powerPlugs': has_power
                }
                
                if edificio not in edifici:
                    edifici[edificio] = []
                edifici[edificio].append(aula)
        
        return edifici
    
    def get_sedi_disponibili(self):
        """Ritorna lista sedi disponibili"""
        return self.sedi


# Funzione di comodo per retrocompatibilità con vecchio codice
def cerca_aule(sede="tutte", giorno=None, ora_inizio="08:15", ora_fine="10:15"):
    """
    Wrapper per mantenere retrocompatibilità con vecchio bot
    """
    scraper = PolimiAuleScraper()
    return scraper.search_aule_libere(sede, giorno, ora_inizio, ora_fine)
