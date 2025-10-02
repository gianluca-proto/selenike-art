# Selenike Art

Selenike Art è un sito vetrina per l'artista Selenike, sviluppato con Flask (Python) e Bootstrap. Il progetto include: una galleria immagini, una pagina per commissioni, una pagina biografica dell'artista, un modulo di contatto, un pannello di amministrazione per la gestione (upload/sync su Cloudinary) e strumenti di sicurezza (autenticazione con token JWT, protezione CSRF, rate limiting e reCAPTCHA).

Questo README è pensato come documento di presentazione da mostrare su GitHub: contiene le informazioni utili per eseguire, testare e valutare il progetto.

---

Indice
- Descrizione
- Tecnologie
- Caratteristiche principali
- Architettura del progetto
- Requisiti
- Installazione locale
- Variabili d'ambiente importanti
- Avvio in sviluppo
- Migrazioni e database
- Test
- Sicurezza e buone pratiche implementate
- Deployment (Heroku / Gunicorn)
- Come presentare/dimostrare il progetto su GitHub
- Contribuire
- Licenza
- Contatti

---

## Descrizione

Sito vetrina per promuovere opere e servizi di commissione dell'artista Selenike. Fornisce un'esperienza utente responsive, gestione di assets multimediali (Cloudinary) e strumenti amministrativi per mantenere la galleria aggiornata.

## Tecnologie
- Python 3.10+ (compatibile con 3.12)
- Flask 3
- Flask-SQLAlchemy, Flask-Migrate
- Flask-WTF (form validation + CSRF)
- Argon2 per hashing password
- PyJWT per token JWT
- Cloudinary per gestione media
- Flask-Babel per localizzazione
- Flask-Limiter per rate limiting
- Flask-Compress, Flask-Caching
- APScheduler per job periodici (sync dei log)

## Caratteristiche principali
- Homepage informativa
- Galleria immagini con filtri per categorie
- Pagina Commissioni con form di richiesta
- Modulo di contatto via email
- Area amministrazione protetta (JWT + token refresh)
- Upload, spostamento ed eliminazione immagini su Cloudinary
- Sincronizzazione periodica di log e file CSV su Cloudinary
- Protezione reCAPTCHA per login amministratore
- Logging accessi e monitoraggio semplice (access.log)

## Architettura del progetto (sintesi)
- app.py: creazione e configurazione dell'app Flask, registrazione blueprint e job scheduler
- config.py: configurazione centrale e funzioni d'aiuto (es. validate_image)
- routes/: blueprint per pagine pubbliche e admin (main.py, admin.py, gallery.py, security.py)
- models/: modelli SQLAlchemy (Admin, RefreshToken, ecc.)
- services/: logica di business e integrazioni (auth, cloudinary, email, security)
- templates/: template Jinja2 per ogni pagina
- static/: asset CSS/JS/immagini
- migrations/: script Alembic per la gestione schema DB

## Requisiti
- Python 3.10 o superiore
- pip
- Un database PostgreSQL (in locale o remoto) o usare una stringa DATABASE_URL
- Account Cloudinary (opzionale per funzioni media)

## Installazione locale (rapida)

1) Clona il repository

```bash
git clone <repo-url>
cd selenike-art
```

2) Crea e attiva un virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

3) Installa le dipendenze

```bash
pip install -r requirements.txt
```

## Variabili d'ambiente (principali)
Imposta un file `.env` nella root del progetto con le variabili principali. Esempio:

```env
APP_SECRET_KEY=una_stringa_lunga_e_casuale
DATABASE_URL=postgresql://user:password@localhost/selenike_art
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USERNAME=user@example.com
MAIL_PASSWORD=secret
RECAPTCHA_SITE_KEY=your_site_key
RECAPTCHA_SECRET_KEY=your_secret_key
CLOUD_NAME=tuo_cloud_name
CLOUD_API_KEY=tuo_api_key
CLOUD_API_SECRET=tuo_api_secret
```

Note:
- `DATABASE_URL`: se non presente, `config.py` usa una stringa di default pensata per Postgres locale.
- Per sviluppo locale puoi impostare `SESSION_COOKIE_SECURE=False` temporaneamente (in `config.py` o tramite una variabile di configurazione) se non usi HTTPS.

## Migrazioni e database

1) Crea le migrazioni iniziali (se devi applicare modifiche al DB):

```bash
flask db init   # solo la prima volta (se migrations/ non esiste o è vuota)
flask db migrate -m "Initial migration"
flask db upgrade
```

(Questo progetto include già una cartella `migrations/` con almeno una migrazione.)

## Avvio in sviluppo

Metodo rapido (usa `app.py` direttamente):

```bash
python app.py
```

Oppure con Flask CLI (se `FLASK_APP` impostata):

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

Per eseguire con Gunicorn (produzione locale / Heroku):

```bash
gunicorn --bind 0.0.0.0:8000 app:app
```

## Test

Il progetto contiene alcuni test nella cartella `tests/`. Per eseguirli:

```bash
pip install -r requirements.txt
pytest -q
```

## Sicurezza (scelte implementate)
- Password hashing: Argon2 (file `GenerateHashPassword.py` mostra come generare un hash)
- Protezione CSRF: Flask-WTF + CSRFProtect
- Token auth: JWT per l'area admin, con supporto a refresh token (modello `RefreshToken`)
- reCAPTCHA: usato nel login admin per ridurre bot e brute-force
- Rate limiting: Flask-Limiter su rotte sensibili
- Header di sicurezza: Content-Security-Policy, X-Frame-Options, X-Content-Type-Options, X-XSS-Protection sono settati in `app.py`
- Cookie sicuri: i cookie di sessione e auth sono impostati HttpOnly, Secure e SameSite (in `config.py` e nelle route admin)

## Deployment (note rapide)
- Il progetto include un `Procfile` per Heroku.
- Esempio di deploy su Heroku:
  - Imposta le config vars su Heroku (tutte le variabili d'ambiente sopra)
  - Push del repo e scale del web dyno
  - Assicurati che `DATABASE_URL` punti a un database Postgres gestito

## Come presentare/dimostrare il progetto su GitHub
- Aggiungi screenshot della homepage, della galleria e del pannello admin nella cartella `docs/` o nella root.
- Crea un file `DEMO.md` con i link (se il sito è deployato) e una breve walkthrough.
- Usa il README per mettere in evidenza: caratteristiche, tech stack, screenshot, istruzioni rapide per provare in locale.
- Eventualmente aggiungi un breve video (GIF o MP4) nella cartella `docs/` che mostra il flusso: visualizzazione galleria → richiesta commissione → login admin → upload immagine (Cloudinary).

Suggerimenti per una presentazione in repository:
- Aggiorna la sezione "Descrizione" con un paio di punti chiave del tuo ruolo e cosa hai implementato (ad es. "Ho implementato autenticazione JWT, integrazione Cloudinary e protezioni anti-bot via reCAPTCHA").
- Metti un badge di test/coverage (se configuri CI)
- Metti un badge di license

## Contribuire
- Aprire issue per bug o richieste di funzionalità
- Fork & pull request: crea un branch per la tua feature e apri PR descrittivo

## Licenza
- Questo progetto può essere rilasciato sotto licenza MIT (o altra a tua scelta). Aggiungi un file `LICENSE` se vuoi esplicitare la licenza.

## Contatti
- Managed by Gianluca Proto
- Per domande o demo live, aggiungi una mail o link di contatto nel README (opzionale).

---

## Stato attuale e note finali
- Il codice presente contiene già integrazione Cloudinary, job di sincronizzazione, supporto i18n (Flask-Babel) e miglioramenti di sicurezza.
- Se vuoi, posso aggiungere al repository:
  - Esempi di `.env.example`
  - Script di deploy automatico
  - Piccoli test aggiuntivi per le funzioni di servizio (Cloudinary, auth)

Buon lavoro — se vuoi che aggiorni il README con screenshot reali o un `DEMO.md` con comandi di deploy passo-passo, dimmelo e lo aggiungo.
