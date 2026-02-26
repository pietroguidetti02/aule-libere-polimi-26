# Report Avanzamenti Bot AuleLiberePoliMi - Gennaio 2026

## 📋 Riepilogo Attività
Il bot è stato completamente aggiornato per funzionare con il nuovo portale del Politecnico di Milano. Il codice è stato adattato per Python 3.13 (in sviluppo) e Python 3.11 (in produzione Docker), risolvendo problemi di dipendenze e di encoding.

## 🛠️ Modifiche Tecniche Principali

### 1. Nuovo Sistema di Scraping (`search/polimi_scraper.py`)
- **Nuovo Endpoint:** Implementata la logica per chiamare `RicercaAuleLibere.do`.
- **Parametri Case-Sensitive:** Corretto un bug critico dove i codici sede (es. "MIA") venivano inviati in minuscolo. Ora il sistema distingue tra "tutte" (minuscolo) e codici sede specifici (maiuscoli).
- **Rilevamento Prese Elettriche:** Implementata estrazione del parametro `idaula` dai link "Vedi dettagli" per confrontarlo con il database `roomsWithPower.json`. Aggiunta emoji 🔌.
- **Raggruppamento Edifici:** La logica di parsing ora raggruppa i risultati per numero edificio (es. "Edificio 11") invece di una lista piatta.

### 2. Aggiornamento Dipendenze e Compatibilità
- **Python-Telegram-Bot:** Downgrade alla versione `13.7` per mantenere la compatibilità con la struttura esistente del codice (ConversationHandler, ecc.).
- **Fix Python 3.13:** Creato un modulo locale `imghdr.py` poiché la libreria standard è stata rimossa nelle nuove versioni di Python.
- **Fix Encoding Windows:** Aggiunto `encoding='utf-8'` in tutte le chiamate `open()` per evitare `UnicodeDecodeError` sui file JSON.
- **Requirements:** Pulito `requirements.txt` rimuovendo librerie problematiche (`regex`) e fissando le versioni corrette.

### 3. Logica Bot e Interfaccia
- **Persistenza Preferenze:** Risolto bug nel salvataggio delle preferenze (Sede, Lingua). Ora il dizionario `context.user_data` viene aggiornato esplicitamente per forzare il salvataggio su disco (`aulelibere_pp`).
- **Formattazione Messaggi:** I risultati sono ora raggruppati visivamente per edificio, con indicazione dell'orario di fine ricerca.
- **Donazioni:** Aggiunto pulsante "☕ Offrimi un caffè" con link PayPal aggiornato.
- **Contatti:** Aggiornato messaggio di errore con la nuova email `pg02.uni@gmail.com`.

## 🐳 Deployment (Docker)

Il progetto è pronto per l'hosting sul tuo server Windows 11 con Docker.

### File Creati
1.  **`Dockerfile`**: Usa `python:3.11-slim` per un'immagine leggera e stabile.
2.  **`docker-compose.yml`**: Configurato per:
    - Riavvio automatico (`restart: always`).
    - Persistenza dati (`volumes`) per non perdere le preferenze degli utenti (`aulelibere_pp`).
    - Limiti risorse (0.5 CPU, 512MB RAM) per proteggere il server.
    - Timezone corretta (`Europe/Rome`).

### Comandi Gestione
- **Avvio/Aggiornamento:**
  ```bash
  docker compose up -d --build
  ```
- **Controllo Log:**
  ```bash
  docker logs -f polimi_bot
  ```
- **Stop:**
  ```bash
  docker compose down
  ```

## 📝 Note per il Futuro
- **Preferenze:** Le preferenze degli utenti sono salvate nel file `aulelibere_pp` nella cartella del progetto. Non cancellare questo file se vuoi mantenere le impostazioni degli utenti.
- **Database Aule:** Se il PoliMi cambia le aule con le prese, aggiornare `json/roomsWithPower.json`.
- **Sedi:** I codici sede sono mappati in `json/location.json`.

---
*Ultimo aggiornamento: 19 Gennaio 2026*
