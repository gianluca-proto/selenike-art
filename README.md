# Selenike Art

Selenike Art è un sito web vetrina creato con Flask e Bootstrap per mostrare e commissionare le opere d'arte di Selenike. Il sito include una galleria d'arte, una sezione per le commissioni, informazioni sull'artista e un modulo di contatto.

## Caratteristiche

- **Homepage**: Introduzione e panoramica delle opere d'arte di Selenike.
- **Art Gallery**: Galleria di immagini con filtri per categoria (animali, fumetti, illustrazioni).
- **Commissions**: Informazioni su come richiedere un'opera su commissione e un modulo di contatto.
- **Selenike**: Informazioni sull'artista e il suo percorso.
- **Contact**: Modulo di contatto per richieste e informazioni.
- **WhatsApp Integration**: Pulsante per contattare l'artista tramite WhatsApp.

## Requisiti

- Python 3.x
- Flask
- Bootstrap
- Ekko-lightbox

## Installazione

1. Clona il repository:

   ```bash
   git clone https://github.com/QuantumCoder-code/selenike-art.git
   ```
2. Naviga nella directory del progetto:

   ```bash
   cd selenike-art
   ```
3. Crea un ambiente virtuale e attivalo:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Su Windows usa .venv\Scripts\activate
   ```
4. Installa le dipendenze:

   ```bash
   pip install -r requirements.txt
   ```
5. Avvia l'applicazione Flask:

   ```bash
   flask run
   ```

## Struttura del Progetto

- `app.py`: File principale dell'applicazione Flask.
- `templates/`: Directory contenente i template HTML.
  - `base.html`: Template base con header, navbar e footer.
  - `index.html`: Template per la homepage.
  - `gallery.html`: Template per la galleria d'arte.
  - `commissions.html`: Template per la sezione commissioni.
  - `about.html`: Template per la sezione informazioni sull'artista.
  - `contact.html`: Template per la sezione contatti.
- `static/`: Directory contenente i file statici (CSS, JS, immagini).

## Utilizzo

### Galleria d'Arte

La galleria d'arte utilizza una funzionalità di filtro per visualizzare diverse categorie di immagini. Le immagini vengono visualizzate in anteprima utilizzando ekko-lightbox.

### Commissioni

La sezione commissioni fornisce informazioni dettagliate su come richiedere un'opera su commissione e include un modulo di contatto per inviare richieste specifiche.

### Modulo di Contatto

La sezione contatti include un modulo che gli utenti possono utilizzare per inviare richieste o domande. I campi includono nome, email, oggetto, tipo di disegno, formato e messaggio.

## Contributi

I contributi sono benvenuti! Se hai idee per migliorare il sito o hai trovato un bug, sentiti libero di aprire una issue o inviare una pull request.

## Licenza

Questo progetto è sotto licenza MIT. Vedi il file [LICENSE](LICENSE) per maggiori dettagli.

## Contatti

Per ulteriori informazioni, visitate [Selenike Art](https://selenikeart.com) o contattateci tramite il modulo di contatto sul sito.

---

Managed by Gianluca Proto.
