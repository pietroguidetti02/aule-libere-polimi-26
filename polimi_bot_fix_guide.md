# Guida Completa: Fix Bot Telegram AuleLiberePoliMi

## 📋 Panoramica

Il bot Telegram per cercare aule libere al Politecnico di Milano non funziona più perché il sistema di gestione aule è cambiato. Questo documento contiene TUTTE le modifiche necessarie per farlo funzionare di nuovo.

## 🎯 Obiettivo

Ripristinare il funzionamento del bot telegram [@auleliberepolimi_bot](https://telegram.me/auleliberepolimi_bot) aggiornando il sistema di scraping al nuovo portale PoliMi.

---

## 📂 Struttura Repository Attuale

```
AuleLiberePoliMi/
├── bot.py                 # File principale del bot
├── search/                # Cartella con logica di ricerca
│   └── [file di scraping]
├── functions/             # Funzioni di supporto
├── json/                  # Dati JSON (probabilmente da aggiornare)
├── photos/                # Immagini per il bot
├── requirements.txt       # Dipendenze Python
├── Pipfile               # Dipendenze Pipenv
└── README.md
```

---

## 🔧 MODIFICHE NECESSARIE

### 1. NUOVO ENDPOINT E PARAMETRI

**CAMBIAMENTO**: Il vecchio sistema PoliMi non esiste più. Il nuovo è su:
- **URL**: `https://onlineservices.polimi.it/spazi/spazi/controller/RicercaAuleLibere.do`
- **Metodo**: POST

**PARAMETRI POST** (form-data):

```python
{
    'jaf_currentWFID': 'main',
    'spazi___model___formbean___RicercaAuleLibereVO___postBack': 'true',
    'spazi___model___formbean___RicercaAuleLibereVO___formMode': 'FILTER',
    'spazi___model___formbean___RicercaAuleLibereVO___sede': 'tutte',  # o codice sede
    'spazi___model___formbean___RicercaAuleLibereVO___giorno_day': '16',
    'spazi___model___formbean___RicercaAuleLibereVO___giorno_month': '1',
    'spazi___model___formbean___RicercaAuleLibereVO___giorno_year': '2026',
    'jaf_spazi___model___formbean___RicercaAuleLibereVO___giorno_date_format': 'dd/MM/yyyy',
    'spazi___model___formbean___RicercaAuleLibereVO___orario_dal': '15:15',
    'spazi___model___formbean___RicercaAuleLibereVO___orario_al': '17:15',
    'evn_ricerca': 'Ricerca aule libere'
}
```

**CODICI SEDI DISPONIBILI**:
```python
SEDI = {
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
```

---

### 2. NUOVA STRUTTURA HTML RISPOSTA

**CAMBIAMENTO**: La risposta HTML ha una struttura completamente diversa.

**NUOVA STRUTTURA**:

```html
<!-- Due tabelle separate -->

<!-- Tabella 1: Aule Studio (id='aulestudiocoll') -->
<div id='div_table_aulestudiocoll'>
    <h4>Risultano X aule dedicate allo studio corrispondenti ai criteri di filtro!</h4>
    <table class='TableDati' id='aulestudiocoll'>
        <tbody class='TableDati-tbody'>
            <tr class='dispari'>
                <td class='TestoSX Dati1'>Milano Città Studi,<br>Piazza Leonardo da Vinci 32</td>
                <td class='TestoSX Dati1'><strong>9.0.3</strong></td>
                <td class='Dati1'><a href="...">Vedi dettagli</a></td>
                <td class='TestoSX Dati1'>AULA DIDATTICA</td>
                <td class='TestoSX Dati1'>PLATEA FRONTALE</td>
                <td class='TestoSX Dati1'>-</td>
            </tr>
            <!-- Altre righe... -->
        </tbody>
    </table>
</div>

<!-- Tabella 2: Aule Normali (id='aule') -->
<div id='div_table_aule'>
    <h4>Risultano X aule libere corrispondenti ai criteri di filtro!</h4>
    <table class='TableDati' id='aule'>
        <tbody class='TableDati-tbody'>
            <!-- Stessa struttura della tabella sopra -->
        </tbody>
    </table>
</div>
```

**COLONNE TABELLA** (6 colonne per riga):
1. **Dove**: Sede e indirizzo (es. "Milano Città Studi, Via Bonardi")
2. **Sigla**: Nome aula in `<strong>` (es. "B.2.1", "BELTRAMI")
3. **Dettagli**: Link "Vedi dettagli" (ignorare)
4. **Categoria**: Tipo aula (es. "AULA DIDATTICA", "LABORATORIO")
5. **Tipologia**: Caratteristiche (es. "PLATEA FRONTALE", "INFORMATIZZATA")
6. **Dipartimento**: Dipartimento o "-"

---

### 3. CODICE PYTHON PER SCRAPING

**FILE DA MODIFICARE**: `search/[nome_file_scraping].py` (o creare nuovo file)

**CODICE COMPLETO**:

```python
import requests
from bs4 import BeautifulSoup
from datetime import datetime


class PolimiAuleScraper:
    """
    Scraper per il nuovo sistema aule libere PoliMi
    """
    
    def __init__(self):
        self.base_url = "https://onlineservices.polimi.it/spazi/spazi/controller/RicercaAuleLibere.do"
        self.session = requests.Session()
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
        params = {
            'jaf_currentWFID': 'main',
            'spazi___model___formbean___RicercaAuleLibereVO___postBack': 'true',
            'spazi___model___formbean___RicercaAuleLibereVO___formMode': 'FILTER',
            'spazi___model___formbean___RicercaAuleLibereVO___sede': sede.lower(),
            'spazi___model___formbean___RicercaAuleLibereVO___giorno_day': str(giorno.day),
            'spazi___model___formbean___RicercaAuleLibereVO___giorno_month': str(giorno.month),
            'spazi___model___formbean___RicercaAuleLibereVO___giorno_year': str(giorno.year),
            'jaf_spazi___model___formbean___RicercaAuleLibereVO___giorno_date_format': 'dd/MM/yyyy',
            'spazi___model___formbean___RicercaAuleLibereVO___orario_dal': ora_dal,
            'spazi___model___formbean___RicercaAuleLibereVO___orario_al': ora_al,
            'evn_ricerca': 'Ricerca aule libere'
        }
        
        try:
            response = self.session.post(self.base_url, data=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            aule_studio = self._parse_tabella(soup, 'aulestudiocoll')
            aule_normali = self._parse_tabella(soup, 'aule')
            
            return {
                'aule_studio': aule_studio,
                'aule_normali': aule_normali,
                'totale': len(aule_studio) + len(aule_normali),
                'sede_nome': self.sedi.get(sede.upper(), 'Tutte'),
                'data': giorno.strftime('%d/%m/%Y'),
                'orario': f"{ora_dal} - {ora_al}"
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
        Estrae aule da una tabella specifica
        
        Args:
            soup: BeautifulSoup object
            table_id: str - 'aulestudiocoll' o 'aule'
        
        Returns:
            list - Lista dizionari con info aule
        """
        aule = []
        
        # Trova la tabella con id specifico
        tabella = soup.find('table', id=table_id)
        if not tabella:
            return aule
        
        tbody = tabella.find('tbody', class_='TableDati-tbody')
        if not tbody:
            return aule
        
        righe = tbody.find_all('tr')
        
        for riga in righe:
            celle = riga.find_all('td')
            if len(celle) >= 6:
                # Colonna 1: Dove (edificio + indirizzo)
                dove_text = celle[0].get_text(separator=' ', strip=True)
                
                # Colonna 2: Sigla (nome aula in <strong>)
                sigla_tag = celle[1].find('strong')
                sigla = sigla_tag.text.strip() if sigla_tag else celle[1].text.strip()
                
                # Colonne 4, 5, 6: Categoria, Tipologia, Dipartimento
                aula = {
                    'sigla': sigla,
                    'dove': dove_text,
                    'categoria': celle[3].text.strip(),
                    'tipologia': celle[4].text.strip(),
                    'dipartimento': celle[5].text.strip()
                }
                aule.append(aula)
        
        return aule
    
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
```

---

### 4. MODIFICHE AL FILE bot.py

**LOCALIZZARE** nel file `bot.py`:

1. **Import vecchio scraper** (cercare linee tipo):
```python
from search.old_scraper import search_aule
# OPPURE
import search.scraper as scraper
```

2. **SOSTITUIRE CON**:
```python
from search.polimi_scraper import PolimiAuleScraper, cerca_aule
```

3. **LOCALIZZARE funzioni di ricerca** (cercare funzioni che chiamano lo scraper)

4. **AGGIORNARE chiamate** esempio:
```python
# VECCHIO (esempio generico)
risultati = vecchia_funzione_ricerca(parametri)

# NUOVO
scraper = PolimiAuleScraper()
risultati = scraper.search_aule_libere(
    sede="MIA",  # o sede scelta dall'utente
    giorno=datetime.now(),
    ora_dal="08:15",
    ora_al="10:15"
)
```

5. **AGGIORNARE formattazione messaggi** (cercare funzioni che creano messaggi telegram):

```python
# ESEMPIO FORMATTAZIONE MESSAGGIO
def formatta_messaggio_risultati(risultati):
    """Crea messaggio Telegram dai risultati"""
    
    if 'errore' in risultati:
        return f"❌ Errore: {risultati['errore']}"
    
    msg = f"📅 *{risultati['data']}* | ⏰ {risultati['orario']}\n"
    msg += f"📍 Sede: {risultati['sede_nome']}\n\n"
    
    if risultati['totale'] == 0:
        return msg + "😔 Nessuna aula libera trovata"
    
    msg += f"✅ *{risultati['totale']} aule libere*\n\n"
    
    # Aule studio
    if risultati['aule_studio']:
        msg += "📚 *Aule Studio*\n"
        for aula in risultati['aule_studio'][:5]:  # Prime 5
            msg += f"• {aula['sigla']} - {aula['dove']}\n"
        if len(risultati['aule_studio']) > 5:
            msg += f"  _...e altre {len(risultati['aule_studio'])-5}_\n"
        msg += "\n"
    
    # Aule normali
    if risultati['aule_normali']:
        msg += "🏫 *Aule Didattiche*\n"
        for aula in risultati['aule_normali'][:10]:  # Prime 10
            msg += f"• {aula['sigla']} - {aula['dove']}\n"
            msg += f"  _{aula['categoria']} | {aula['tipologia']}_\n"
        if len(risultati['aule_normali']) > 10:
            msg += f"  _...e altre {len(risultati['aule_normali'])-10}_\n"
    
    return msg
```

---

### 5. AGGIORNAMENTO requirements.txt

**VERIFICARE** che `requirements.txt` contenga:

```txt
beautifulsoup4>=4.12.0
requests>=2.31.0
python-telegram-bot>=13.0
python-dotenv>=1.0.0
```

**SE MANCANTI**, aggiungere.

---

### 6. FILE JSON DA AGGIORNARE (se presenti)

**LOCALIZZARE** file JSON in `/json/` che potrebbero contenere:
- Lista vecchie aule
- Edifici
- Mapping sedi

**AGGIORNARE** con nuovi codici sede:

```json
{
  "sedi": {
    "tutte": "Tutte le sedi",
    "COE": "Como",
    "CRG": "Cremona",
    "GEM": "Genova",
    "LCF": "Lecco",
    "MNI": "Mantova",
    "MIB": "Milano Bovisa",
    "MIA": "Milano Città Studi",
    "MIF": "Milano Tortona",
    "PCL": "Piacenza",
    "MIC": "Servizi",
    "MID": "Sesto Ulteriano"
  }
}
```

---

### 7. COMANDI BOT DA VERIFICARE/AGGIORNARE

**LOCALIZZARE** in `bot.py` la definizione dei comandi (cercare `@bot.command` o `CommandHandler`):

**COMANDI MINIMI NECESSARI**:

```python
/start - Avvia il bot
/cerca - Cerca aule libere
/oggi - Aule libere oggi
/domani - Aule libere domani
/sede - Scegli sede
/help - Guida uso bot
```

**ESEMPIO HANDLER COMANDO /cerca**:

```python
def cerca_command(update, context):
    """Handler comando /cerca"""
    
    # Mostra tastiera inline per scegliere sede
    keyboard = [
        [InlineKeyboardButton("Milano Città Studi", callback_data='sede_MIA')],
        [InlineKeyboardButton("Milano Bovisa", callback_data='sede_MIB')],
        [InlineKeyboardButton("Tutte le sedi", callback_data='sede_tutte')],
        # ... altre sedi
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Scegli la sede:', reply_markup=reply_markup)

def callback_sede(update, context):
    """Handler callback selezione sede"""
    query = update.callback_query
    sede_code = query.data.split('_')[1]  # Estrae codice da 'sede_MIA'
    
    # Esegui ricerca
    scraper = PolimiAuleScraper()
    risultati = scraper.search_aule_libere(
        sede=sede_code,
        giorno=datetime.now(),
        ora_dal="08:15",
        ora_al="20:15"
    )
    
    # Invia risultati
    messaggio = formatta_messaggio_risultati(risultati)
    query.answer()
    query.edit_message_text(text=messaggio, parse_mode='Markdown')
```

---

## 🧪 TEST E VERIFICA

### Test Manuale Scraper

Creare file `test_scraper.py`:

```python
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
```

**ESEGUIRE**:
```bash
python test_scraper.py
```

**OUTPUT ATTESO**:
```
=== TEST 1: Tutte le sedi, oggi ===
Aule trovate: 215
Aule studio: 7
Aule normali: 208

=== TEST 2: Milano Città Studi ===
Aule trovate: 120

=== TEST 3: Orario 15:15-17:15 ===
Aule trovate: 215

Prime 3 aule:
  - 9.0.3: Milano Città Studi, Piazza Leonardo da Vinci 32
  - G.3: Milano Città Studi, Via Bonardi
  - B8 2.3: Milano Bovisa, Via Durando
```

---

## 📝 CHECKLIST IMPLEMENTAZIONE

**PRIMA DI INIZIARE**:
- [ ] Backup completo repository
- [ ] Python 3.7+ installato
- [ ] Dipendenze installate (`pip install -r requirements.txt`)

**MODIFICHE CODICE**:
- [ ] Creare `search/polimi_scraper.py` con nuovo scraper
- [ ] Aggiornare import in `bot.py`
- [ ] Aggiornare funzioni ricerca in `bot.py`
- [ ] Aggiornare formattazione messaggi
- [ ] Aggiornare file JSON sedi (se presenti)
- [ ] Aggiornare `requirements.txt` (se necessario)

**TEST**:
- [ ] Test scraper standalone (`test_scraper.py`)
- [ ] Test bot in locale (comando `/start`)
- [ ] Test ricerca aule (comando `/cerca`)
- [ ] Test con diverse sedi
- [ ] Test con diversi orari

**DEPLOY**:
- [ ] Push su GitHub
- [ ] Deploy su Heroku/server
- [ ] Verifica bot funzionante in produzione

---

## 🚨 PROBLEMI COMUNI E SOLUZIONI

### Problema: "Nessuna aula trovata" sempre

**CAUSA**: Parametri errati o sessione scaduta

**SOLUZIONE**:
```python
# Aggiungere headers alla richiesta
self.session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})
```

### Problema: Timeout richieste

**CAUSA**: Server PoliMi lento

**SOLUZIONE**:
```python
response = self.session.post(self.base_url, data=params, timeout=30)  # Aumenta timeout
```

### Problema: HTML parsing fallisce

**CAUSA**: Struttura HTML cambiata

**SOLUZIONE**:
1. Fare richiesta manuale e salvare HTML
2. Ispezionare struttura con BeautifulSoup
3. Aggiornare selettori CSS

### Problema: Bot non risponde

**CAUSA**: Token Telegram non valido o handler errati

**SOLUZIONE**:
1. Verificare token in file `.env`
2. Verificare handler registrati correttamente
3. Controllare log errori

---

## 📊 STRUTTURA DATI RISPOSTA

**Oggetto ritornato da `search_aule_libere()`**:

```python
{
    'aule_studio': [
        {
            'sigla': '9.0.3',
            'dove': 'Milano Città Studi, Piazza Leonardo da Vinci 32',
            'categoria': 'AULA DIDATTICA',
            'tipologia': 'PLATEA FRONTALE',
            'dipartimento': '-'
        },
        # ... altre aule studio
    ],
    'aule_normali': [
        {
            'sigla': 'BELTRAMI',
            'dove': 'Milano Città Studi, Piazza Leonardo da Vinci 32',
            'categoria': 'AULA DIDATTICA',
            'tipologia': 'PLATEA FRONTALE',
            'dipartimento': '-'
        },
        # ... altre aule normali
    ],
    'totale': 215,
    'sede_nome': 'Tutte',
    'data': '16/01/2026',
    'orario': '15:15 - 17:15',
    'errore': None  # Presente solo in caso di errore
}
```

---

## 🎓 FUNZIONALITÀ OPZIONALI CONSIGLIATE

### 1. Filtro per tipologia
```python
def filtra_per_tipologia(aule, tipologia):
    """Filtra aule per tipologia (es: solo INFORMATIZZATA)"""
    return [a for a in aule if tipologia.upper() in a['tipologia'].upper()]
```

### 2. Ricerca aula specifica
```python
def cerca_aula_specifica(sigla):
    """Cerca disponibilità di un'aula specifica"""
    # Implementare ricerca con sigla
    pass
```

### 3. Notifiche aule libere
```python
def imposta_notifica(user_id, sede, orario):
    """Imposta notifica giornaliera aule libere"""
    # Implementare sistema notifiche
    pass
```

---

## 📚 RISORSE UTILI

- **Repository originale**: https://github.com/feDann/AuleLiberePoliMi
- **Portale PoliMi Spazi**: https://onlineservices.polimi.it/spazi/
- **python-telegram-bot docs**: https://python-telegram-bot.readthedocs.io/
- **BeautifulSoup docs**: https://www.crummy.com/software/BeautifulSoup/bs4/doc/

---

## ✅ RIEPILOGO FINALE

**MODIFICHE PRINCIPALI**:
1. Nuovo scraper con endpoint aggiornato
2. Nuovi parametri POST
3. Nuovo parser HTML per tabelle
4. Aggiornamento comandi bot
5. Nuova formattazione messaggi
6. Dopo ogni richiesta metti un tasto su telegram di "Donate" che cliccando sopra porta al mio PayPal cosi qualcuno può offrire qualcosa

**FILE MODIFICATI**:
- `search/polimi_scraper.py` (NUOVO)
- `bot.py` (MODIFICHE import e handler)
- `json/sedi.json` (SE ESISTE - aggiornamento codici)
- `requirements.txt` (VERIFICA dipendenze)


---

*Documento creato: Gennaio 2026*  
*Versione: 1.0*  
*Testato su: Python 3.9+*