from flask import Blueprint, render_template, request, jsonify  # rimosso abort
import os
from math import ceil
from collections import defaultdict
import re
import json
import logging
from pathlib import Path
import fcntl
import tempfile
from datetime import datetime, timezone, timedelta
import ipaddress
import csv
from services.cloudinary_service import upload_file_to_cloudinary, upload_all_logs_to_cloudinary, download_file_from_cloudinary

try:
    from user_agents import parse as ua_parse
except Exception:
    ua_parse = None

bp = Blueprint('security', __name__)

logger = logging.getLogger(__name__)

# Config/admin token (opzionale). Se ADMIN_API_KEY è impostato, le chiamate admin devono includere header X-Admin-Token
ADMIN_API_KEY = os.getenv('ADMIN_API_KEY')

# Thresholds per aggiornamento della mappa (opzione A)
MIN_COUNT_TO_SWITCH = int(os.getenv('MIN_COUNT_TO_SWITCH', '3'))
SWITCH_RATIO = float(os.getenv('SWITCH_RATIO', '0.66'))

DEVICE_MAP_PATH = Path('instance') / 'device_map.json'
VISITS_HISTORY_PATH = Path('visits_history.csv')

# se impostato, include gli IP loopback nelle statistiche (per i test o per debug)
INCLUDE_LOOPBACK = os.getenv('INCLUDE_LOOPBACK', '') == '1'


def _now_iso():
    # timezone-aware ISO 8601 UTC timestamp
    return datetime.now(timezone.utc).isoformat()


def _classify_device_from_ua(ua_string):
    """Classifica in desktop/mobile/tablet usando user-agents se disponibile, altrimenti heuristica semplice.
    Ritorna None se ua_string è mancante o non valida.
    """
    if not ua_string:
        return None
    s = ua_string.lower()
    # se abbiamo la libreria
    if ua_parse:
        try:
            ua = ua_parse(ua_string)
            if ua.is_tablet:
                return 'tablet'
            if ua.is_mobile:
                return 'mobile'
            return 'desktop'
        except Exception:
            pass
    # fallback semplice
    if 'ipad' in s or 'tablet' in s:
        return 'tablet'
    if 'iphone' in s or 'android' in s or 'mobile' in s:
        return 'mobile'
    return 'desktop'


def _is_bot(ua_string):
    """Rileva UA di bot usando semplici keyword heuristics."""
    if not ua_string:
        return False
    s = ua_string.lower()
    bot_indicators = [
        'bot', 'crawl', 'spider', 'wget', 'curl', 'python-requests', 'headless',
        'monitor', 'uptime', 'checker', 'scan', 'health', 'statuscake', 'pingdom',
        'facebookexternalhit', 'bingpreview', 'slurp', 'mediapartners-google', 'googlebot'
    ]
    for b in bot_indicators:
        if b in s:
            return True
    return False


def _atomic_write(path: Path, content: str):
    """Scrive atomically il contenuto su disco con lock (flock) per evitare corse."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name, text=True)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            # acquisisci lock sul file temporaneo per essere sicuri
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            except Exception:
                pass
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        # rename atomico
        os.replace(tmp, str(path))
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except Exception:
                pass


def _load_device_map():
    try:
        if DEVICE_MAP_PATH.exists():
            data = json.loads(DEVICE_MAP_PATH.read_text(encoding='utf-8'))
            # normalize old format (ip->device string) to new structure
            first_key = next(iter(data.keys()), None)
            if first_key and isinstance(data[first_key], str):
                # convert
                new = {}
                for ip, dev in data.items():
                    new[ip] = {
                        'device': dev,
                        'counts': {dev: 1},
                        'first_seen': None,
                        'last_seen': None,
                        'last_updated': None
                    }
                return new
            return data
    except Exception:
        pass
    return {}


def _save_device_map(m):
    try:
        content = json.dumps(m, ensure_ascii=False, indent=2)
        _atomic_write(DEVICE_MAP_PATH, content)
    except Exception:
        pass


def _extract_from_line(line):
    """Estrae ip, request_path, raw_device, timestamp_str da una riga del log.
    Restituisce tuple (ip, request_path, raw_device, ts_str)
    """
    ip = None
    request_path = None
    raw_device = None
    ts = None
    parts = line.split(' - ')
    # timestamp in parts[0] se presente
    if parts:
        ts = parts[0]
    try:
        if len(parts) > 2 and 'IP:' in parts[2]:
            ip = parts[2].split('IP: ', 1)[1].strip()
    except Exception:
        ip = None
    if not ip:
        m = re.search(r"(\d{1,3}(?:\.\d{1,3}){3})", line)
        if m:
            ip = m.group(1)
    # normalizza ip (rimuove eventuale porta numerica e spazi)
    if ip:
        ip = ip.strip()
        # rimuovi eventuali parentesi per IPv6 come [::1]:5000
        if ip.startswith('[') and ']' in ip:
            inner = ip.split(']', 1)[0][1:]
            ip = inner
        else:
            # rimuove solo se c'è una porta numerica alla fine (es 1.2.3.4:5000)
            mport = re.match(r'^(.*?):(\d+)$', ip)
            if mport:
                ip = mport.group(1)
    try:
        if len(parts) > 3 and 'Request:' in parts[3]:
            raw_req = parts[3].split('Request: ', 1)[1].strip()
            # raw_req può essere "GET /path" o solo "/path"; estraiamo il path
            # gestione semplice: se contiene spazio, prendi la parte dopo il primo spazio
            if ' ' in raw_req:
                # es. "GET /foo?bar" -> "/foo?bar"
                request_path = raw_req.split(' ', 1)[1].strip()
            else:
                request_path = raw_req
    except Exception:
        request_path = None
    if 'Device:' in line:
        try:
            raw_device = line.split('Device: ', 1)[1].strip()
        except Exception:
            raw_device = None
    else:
        possible = parts[-1] if parts else ''
        # fallback: consideriamo possibile UA solo se contiene indicatori tipici di user-agent
        if len(possible) > 20:
            ua_indicators = ['mozilla', 'curl', 'android', 'iphone', 'mobile', 'safari', 'chrome', 'edg', 'firefox']
            s_low = possible.lower()
            if any(ind in s_low for ind in ua_indicators):
                raw_device = possible
            else:
                raw_device = None
    return ip, request_path, raw_device, ts


def _process_lines_update_map(lines):
    """Aggiorna la mappa persistente con logica A (first-seen + soglia per aggiornamento).
    Restituisce la mappa aggiornata.
    """
    device_map = _load_device_map()
    updated = False
    for line in lines:
        ip, request_path, raw_device, ts = _extract_from_line(line)
        if not ip:
            continue
        # Escludi polling/static requests e le richieste dell'area di admin/dashboard
        if request_path and (request_path.startswith('/antro-1986/security') or request_path.startswith('/static/') or request_path.startswith('/favicon.ico')):
            continue
        # Escludi bot
        if raw_device and _is_bot(raw_device):
            continue
        dev_type = _classify_device_from_ua(raw_device)
        if not dev_type:
            continue
        entry = device_map.get(ip)
        if not entry:
            # create new entry
            device_map[ip] = {
                'device': dev_type,
                'counts': {dev_type: 1},
                'first_seen': ts or _now_iso(),
                'last_seen': ts or _now_iso(),
                'last_updated': None
            }
            updated = True
            try:
                logger.info('device-map add: ip=%s device=%s first_seen=%s', ip, dev_type, device_map[ip]['first_seen'])
            except Exception:
                pass
            continue
        # update existing counts and timestamps
        counts = entry.get('counts') or {}
        counts[dev_type] = counts.get(dev_type, 0) + 1
        entry['counts'] = counts
        entry['last_seen'] = ts or _now_iso()
        # decide se cambiare device registrato: se il nuovo dev raggiunge soglia
        current = entry.get('device')
        if dev_type != current:
            total = sum(counts.values())
            if counts[dev_type] >= MIN_COUNT_TO_SWITCH and counts[dev_type] >= int(SWITCH_RATIO * total):
                entry['device'] = dev_type
                entry['last_updated'] = _now_iso()
                updated = True
                try:
                    logger.info('device-map switch: ip=%s old=%s new=%s counts=%s', ip, current, dev_type, counts)
                except Exception:
                    pass
    if updated:
        _save_device_map(device_map)
        try:
            logger.info('device-map persisted entries=%d', len(device_map))
        except Exception:
            pass
    return device_map


def _normalize_ip_str(ip_str):
    """Normalizza e valida una stringa IP; ritorna la forma canonica (str) o None se non valida."""
    if not ip_str:
        return None
    s = str(ip_str).strip()
    # se IPv6 racchiuso tra parentesi [::1] oppure [::1]:5000 -> estrai interno
    if s.startswith('[') and ']' in s:
        inner = s.split(']', 1)[0][1:]
        s = inner
    # Se sembra un IPv4 o IPv4:porta (contiene punti), rimuovi eventuale porta dopo l'ultimo ':'
    if '.' in s:
        if ':' in s:
            head, tail = s.rsplit(':', 1)
            if tail.isdigit():
                s = head
        try:
            ip = ipaddress.ip_address(s)
            return str(ip)
        except Exception:
            # fallback: se la stringa contiene cifre e punti (es. 127.0.XX.XX) consideriamola comunque
            # come chiave normalizzata (non valida come IP reale ma utile per il conteggio).
            if re.search(r"\d", s) and '.' in s:
                return s
            return None
    # probabile IPv6 senza parentesi
    try:
        ip = ipaddress.ip_address(s)
        return str(ip)
    except Exception:
        # fallback: se contiene cifre e due punti (es. formati IPv6 parziali), ritorniamo la stringa
        if re.search(r"\d", s) and ':' in s:
            return s
        return None


def _counts_from_map(m: dict):
    """Dalla mappa persistente (device_map) ritorna un conteggio per device normalizzando IP.

    Strategia:
    - normalizza ogni chiave usando _normalize_ip_str
    - raggruppa le voci con la stessa chiave normalizzata
    - per ogni gruppo, seleziona l'entry con `last_seen` più recente (gestisce formati ISO/Z e fallback)
    - restituisce dizionario counts {'mobile': X, 'desktop': Y, 'tablet': Z}
    """
    if not isinstance(m, dict):
        return {'mobile': 0, 'desktop': 0, 'tablet': 0}

    def _parse_ts(ts):
        if not ts:
            return None
        if isinstance(ts, datetime):
            return ts
        s = str(ts).strip()
        # try common ISO formats
        for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
            try:
                # handle trailing Z as UTC
                if s.endswith('Z') and '%z' not in fmt:
                    return datetime.strptime(s, fmt)
                return datetime.strptime(s, fmt)
            except Exception:
                continue
        try:
            # last resort: fromisoformat (python 3.11+ tolerates many forms)
            return datetime.fromisoformat(s)
        except Exception:
            return None

    grouped = {}
    for raw_key, entry in (m.items() if isinstance(m, dict) else []):
        norm = _normalize_ip_str(raw_key)
        if not norm:
            # ignora chiavi non normalizzabili
            continue
        # scegli entry con last_seen più recente
        cur = grouped.get(norm)
        cur_ts = _parse_ts(cur.get('last_seen')) if cur else None
        ent_ts = _parse_ts(entry.get('last_seen'))
        # se cur è None -> prendi entry
        take = False
        if cur is None:
            take = True
        else:
            # se ent_ts è None non sostituiamo; se cur_ts è None prendiamo ent
            if ent_ts and cur_ts:
                if ent_ts > cur_ts:
                    take = True
            elif ent_ts and not cur_ts:
                take = True
            # else mantieni cur
        if take:
            grouped[norm] = entry

    counts = {'mobile': 0, 'desktop': 0, 'tablet': 0}
    for entry in grouped.values():
        d = entry.get('device') if isinstance(entry, dict) else None
        if d in counts:
            counts[d] += 1
        else:
            counts['desktop'] += 1
    return counts


def _counts_from_lines_unique_ips(lines, include_loopback=None):
    """Conta una entry per ogni combinazione IP+device (non solo per IP).
    Filtra richieste statiche e bot come nella versione precedente.
    Se il device non è riconosciuto, conta comunque come 'desktop'.
    """
    seen = set()
    device_counts = {'mobile': 0, 'desktop': 0, 'tablet': 0}
    for line in lines:
        ip, request_path, raw_device, ts = _extract_from_line(line)
        if not ip:
            continue
        # Escludi polling/static requests e le richieste dell'area di admin/dashboard
        if request_path and (request_path.startswith('/antro-1986/security') or request_path.startswith('/static/') or request_path.startswith('/favicon.ico')):
            continue
        # Escludi bot
        if raw_device and _is_bot(raw_device):
            continue
        norm = _normalize_ip_str(ip)
        if not norm:
            continue
        # escludi loopback a meno che non sia esplicitamente abilitato
        use_loopback = INCLUDE_LOOPBACK if include_loopback is None else bool(include_loopback)
        if not use_loopback:
            try:
                nip = ipaddress.ip_address(norm)
                if nip.is_loopback:
                    continue
            except Exception:
                if norm in ('127.0.0.1', '::1'):
                    continue
        dev_type = _classify_device_from_ua(raw_device)
        if not dev_type:
            dev_type = 'desktop'  # fallback
        key = (norm, dev_type)
        if key in seen:
            continue
        seen.add(key)
        if dev_type in device_counts:
            device_counts[dev_type] += 1
        else:
            device_counts['desktop'] += 1
    return device_counts


def _stats_from_lines(lines, sample=20):
    """Restituisce diagnostica: counts, numero unico di IP conteggiati, righe totali ed escluse e una sample degli IP visti."""
    total = len(lines)
    seen = {}
    excluded = 0
    for line in lines:
        ip, request_path, raw_device, ts = _extract_from_line(line)
        if not ip:
            excluded += 1
            continue
        if request_path and (request_path.startswith('/antro-1986/security') or request_path.startswith('/static/') or request_path.startswith('/favicon.ico')):
            excluded += 1
            continue
        if raw_device and _is_bot(raw_device):
            excluded += 1
            continue
        norm = _normalize_ip_str(ip)
        if not norm:
            excluded += 1
            continue
        if norm in seen:
            continue
        dev_type = _classify_device_from_ua(raw_device)
        if not dev_type:
            excluded += 1
            continue
        seen[norm] = {'device': dev_type, 'raw_ua': raw_device, 'request': request_path, 'ts': ts}

    counts = {'mobile': 0, 'desktop': 0, 'tablet': 0}
    for dev in seen.values():
        d = dev['device']
        if d in counts:
            counts[d] += 1
        else:
            counts['desktop'] += 1

    sample_items = dict(list(seen.items())[:sample])
    return {
        'counts': counts,
        'unique_ips': len(seen),
        'total_lines': total,
        'excluded_lines': excluded,
        'sample_seen': sample_items
    }


def _visits_timeseries_from_lines(lines):
    """Ritorna (labels, data) dove labels sono date YYYY-MM-DD ordinate e data è il numero di visitatori unici (IP) per giorno.
    """
    per_day = defaultdict(set)
    for line in lines:
        ip, request_path, raw_device, ts = _extract_from_line(line)
        if not ip:
            continue
        # Escludi richieste dashboard/statics
        if request_path and (request_path.startswith('/antro-1986/security') or request_path.startswith('/static/') or request_path.startswith('/favicon.ico')):
            continue
        if raw_device and _is_bot(raw_device):
            continue
        norm = _normalize_ip_str(ip)
        if not norm:
            continue
        if not INCLUDE_LOOPBACK:
            try:
                nip = ipaddress.ip_address(norm)
                if nip.is_loopback:
                    continue
            except Exception:
                if norm in ('127.0.0.1', '::1'):
                    continue
        if not ts:
            continue
        # parse timestamp come 'YYYY-mm-dd HH:MM:SS,fff'
        try:
            dt = datetime.strptime(ts.strip(), '%Y-%m-%d %H:%M:%S,%f')
        except Exception:
            try:
                dt = datetime.fromisoformat(ts)
            except Exception:
                continue
        day = dt.date().isoformat()
        per_day[day].add(norm)

    labels = sorted(per_day.keys())
    data = [len(per_day[d]) for d in labels]
    return labels, data


def _read_visits_history():
    """Legge lo storico delle visite giornaliere dal file CSV."""
    history = {}
    if VISITS_HISTORY_PATH.exists():
        with open(VISITS_HISTORY_PATH, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if not row or row[0].startswith('#') or row[0] == 'data':
                    continue
                try:
                    history[row[0]] = int(row[1])
                except Exception:
                    continue
    return history


def _append_visit_to_history(date_str, visits):
    """Aggiunge una riga allo storico in modo atomico, solo se la data non è già presente. Esegue upload su Cloudinary."""
    # Scarica sempre la versione più aggiornata prima di modificare
    download_file_from_cloudinary('stats/visits_history.csv', str(VISITS_HISTORY_PATH))
    history = _read_visits_history()
    if date_str in history:
        return  # già presente
    # Scrivi in modo atomico
    lines = []
    if VISITS_HISTORY_PATH.exists():
        with open(VISITS_HISTORY_PATH, encoding='utf-8') as f:
            lines = f.readlines()
    with open(VISITS_HISTORY_PATH, 'a', encoding='utf-8') as f:
        if not lines:
            f.write('data,visite\n')
        f.write(f'{date_str},{visits}\n')
    # Upload automatico su Cloudinary
    upload_file_to_cloudinary(str(VISITS_HISTORY_PATH), folder="stats")
    _upload_logs_to_cloudinary()


def _update_visits_history_from_logs(log_lines):
    """Aggiorna lo storico delle visite giornaliere con i dati del giorno precedente, se mancante."""
    history = _read_visits_history()
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    yest_str = yesterday.isoformat()
    if yest_str in history:
        return  # già presente
    # Calcola visite uniche di ieri dai log
    per_day = defaultdict(set)
    for line in log_lines:
        ip, request_path, raw_device, ts = _extract_from_line(line)
        if not ip or not ts:
            continue
        # Escludi richieste dashboard/statics
        if request_path and (request_path.startswith('/antro-1986/security') or request_path.startswith('/static/') or request_path.startswith('/favicon.ico')):
            continue
        if raw_device and _is_bot(raw_device):
            continue
        norm = _normalize_ip_str(ip)
        try:
            dt = datetime.fromisoformat(ts)
        except Exception:
            continue
        if dt.date() == yesterday:
            per_day[yest_str].add(norm)
    visits = len(per_day[yest_str])
    if visits > 0:
        _append_visit_to_history(yest_str, visits)


def _upload_logs_to_cloudinary():
    """Carica tutti i file access.log* su Cloudinary nella cartella logs/."""
    try:
        upload_all_logs_to_cloudinary(log_dir=".", pattern="access.log", folder="logs")
    except Exception as e:
        print(f"Errore upload log su Cloudinary: {e}")


@bp.route('/antro-1986/security-dashboard')
def security_dashboard():
    # Sincronizza visits_history.csv da Cloudinary all'avvio della dashboard
    download_file_from_cloudinary('stats/visits_history.csv', str(VISITS_HISTORY_PATH))
    # Forza upload file log e csv su Cloudinary ad ogni caricamento
    if VISITS_HISTORY_PATH.exists():
        url = upload_file_to_cloudinary(str(VISITS_HISTORY_PATH), folder="stats")
        _upload_logs_to_cloudinary()
    else:
        print("[DEBUG] visits_history.csv non esiste, nessun upload.")
    print("[DEBUG] Tentativo upload access.log* su Cloudinary...")
    _upload_logs_to_cloudinary()
    print("[DEBUG] Upload access.log* completato (vedi eventuali errori sopra).")

    # paginazione: pagina e per_page
    page = max(1, int(request.args.get('page', 1)))
    per_page = max(10, int(request.args.get('per_page', 100)))

    log_lines = []
    counts = {'mobile': 0, 'desktop': 0, 'tablet': 0}
    visits_labels = []
    visits_data = []

    MAX_GRAPH_LINES = 2000  # Limite righe per i grafici

    try:
        with open('access.log', 'r') as log:
            raw_lines = [l.rstrip('\n') for l in log.readlines() if l.strip()]
            total = len(raw_lines)
            # invertiamo per mostrare prima le righe più recenti
            reversed_lines = list(reversed(raw_lines))
            # paginazione
            start = (page - 1) * per_page
            end = page * per_page
            page_lines = reversed_lines[start:end]

            # --- OTTIMIZZAZIONE: usa solo le ultime N righe per i grafici ---
            graph_lines = raw_lines[-MAX_GRAPH_LINES:] if len(raw_lines) > MAX_GRAPH_LINES else raw_lines
            counts = _counts_from_lines_unique_ips(graph_lines)
            try:
                visits_labels, visits_data = _visits_timeseries_from_lines(graph_lines)
            except Exception:
                visits_labels, visits_data = [], []

            # --- comportamento semplice: usiamo i conteggi correnti dalle ultime righe ---
            # counts è già calcolato sopra con _counts_from_lines_unique_ips(graph_lines)

            # Calcola i totali aggregati dalla device_map (utile per visualizzare subito i totali)
            device_totals = {'mobile': 0, 'desktop': 0, 'tablet': 0}
            try:
                dm = _load_device_map()
                if isinstance(dm, dict):
                    for entry in dm.values():
                        c = entry.get('counts') if isinstance(entry, dict) else {}
                        if not isinstance(c, dict):
                            continue
                        for k, v in c.items():
                            if k in device_totals:
                                try:
                                    device_totals[k] += int(v)
                                except Exception:
                                    pass
                            else:
                                try:
                                    device_totals['desktop'] += int(v)
                                except Exception:
                                    pass
            except Exception:
                device_totals = {'mobile': 0, 'desktop': 0, 'tablet': 0}

            # Prepariamo le righe della pagina come strutture (dizionari) per il template
            log_rows = []
            debug_printed = False
            for line in page_lines:
                parts = line.split(' - ')
                # Prova a estrarre timestamp se la prima parte sembra una data/ora
                possible_ts = parts[0].strip() if parts else ''
                timestamp = 'N/A'
                # Riconosci formato tipo 'YYYY-MM-DD HH:MM:SS,ms'
                import re
                if re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(,\d+)?$", possible_ts):
                    timestamp = possible_ts
                if len(parts) == 5:
                    # Nuovo formato: timestamp - ip - status - url - user_agent
                    ip = parts[1].strip() if parts[1].strip() else 'N/A'
                    status = parts[2].strip() if parts[2].strip() else 'N/A'
                    request_url = parts[3].strip() if parts[3].strip() else 'N/A'
                    raw_device = parts[4].strip() if parts[4].strip() else 'N/A'
                    device_type = _classify_device_from_ua(raw_device)
                    log_rows.append({
                        'timestamp': timestamp,
                        'ip': ip,
                        'request': request_url,
                        'status': status,
                        'raw_device': raw_device,
                        'device_type': device_type
                    })
                elif len(parts) == 4:
                    # Vecchio formato senza timestamp
                    ip = parts[0].strip() if parts[0].strip() else 'N/A'
                    status = parts[1].strip() if parts[1].strip() else 'N/A'
                    request_url = parts[2].strip() if parts[2].strip() else 'N/A'
                    raw_device = parts[3].strip() if parts[3].strip() else 'N/A'
                    device_type = _classify_device_from_ua(raw_device)
                    log_rows.append({
                        'timestamp': 'N/A',
                        'ip': ip,
                        'request': request_url,
                        'status': status,
                        'raw_device': raw_device,
                        'device_type': device_type
                    })
                elif len(parts) >= 5:
                    timestamp = parts[0]
                    ip = 'N/A'
                    request_url = 'N/A'
                    status = 'N/A'
                    raw_device = None
                    try:
                        if 'IP:' in parts[2]:
                            ip = parts[2].split('IP: ', 1)[1].strip()
                    except Exception:
                        ip = 'N/A'
                    try:
                        if 'Request:' in parts[3]:
                            request_url = parts[3].split('Request: ', 1)[1].strip()
                    except Exception:
                        request_url = parts[3] if parts[3] else 'N/A'
                    try:
                        if 'Response:' in parts[4]:
                            status = parts[4].split('Response: ', 1)[1].strip()
                    except Exception:
                        status = parts[4] if parts[4] else 'N/A'
                    if len(parts) > 5 and 'Device:' in parts[5]:
                        try:
                            raw_device = parts[5].split('Device: ', 1)[1].strip()
                        except Exception:
                            raw_device = parts[5]
                    else:
                        possible = parts[-1]
                        if len(possible) > 20:
                            raw_device = possible
                    device_type = _classify_device_from_ua(raw_device)
                    log_rows.append({
                        'timestamp': timestamp,
                        'ip': ip,
                        'request': request_url,
                        'status': status,
                        'raw_device': raw_device or 'N/A',
                        'device_type': device_type
                    })
                else:
                    log_rows.append({
                        'timestamp': 'N/A',
                        'ip': 'N/A',
                        'request': 'N/A',
                        'status': 'N/A',
                        'raw_device': 'N/A',
                        'device_type': 'N/A'
                    })

            log_lines = log_rows
            total_pages = max(1, ceil(total / per_page))
    except FileNotFoundError:
        # Restituisci comunque una lista di righe strutturate per il template
        log_lines = [{
            'timestamp': 'N/D',
            'ip': 'N/D',
            'request': 'Nessun log disponibile',
            'status': 'N/D',
            'raw_device': 'N/D',
            'device_type': 'N/D'
        }]
        total = 0
        total_pages = 1

    # --- Aggiunta gestione storico visite giornaliere ---
    history = _read_visits_history()
    visits_labels = list(sorted(history.keys()))
    visits_data = [history[d] for d in visits_labels]
    today = datetime.now().date().isoformat()
    # Calcola visite oggi dai log
    per_day = defaultdict(set)
    for line in raw_lines:
        ip, request_path, raw_device, ts = _extract_from_line(line)
        if not ip or not ts:
            continue
        if request_path and (request_path.startswith('/antro-1986/security') or request_path.startswith('/static/') or request_path.startswith('/favicon.ico')):
            continue
        if raw_device and _is_bot(raw_device):
            continue
        norm = _normalize_ip_str(ip)
        try:
            dt = datetime.fromisoformat(ts)
        except Exception:
            continue
        if dt.date().isoformat() == today:
            per_day[today].add(norm)
    # Aggiungi oggi se non già presente
    if today not in visits_labels:
        visits_labels.append(today)
        visits_data.append(len(per_day[today]))

    return render_template('antro-1986/security_dashboard.html',
                           log_lines=log_lines,
                           counts=counts,
                           device_totals=device_totals,
                           visits={'labels': visits_labels, 'data': visits_data},
                           page=page,
                           per_page=per_page,
                           total_pages=total_pages)


@bp.route('/antro-1986/security-stats')
def security_stats():
    """Endpoint JSON per i conteggi (utile per polling dal client).
    Supporta query param 'day=yesterday' per ottenere i conteggi filtrati alle righe di ieri.
    Includiamo SEMPRE il loopback per ambiente locale/sviluppo.
    """
    counts = {'mobile': 0, 'desktop': 0, 'tablet': 0}
    MAX_GRAPH_LINES = 2000  # Limite righe per i grafici anche per il polling
    day = request.args.get('day')
    target_date = None
    if day == 'yesterday':
        # calcola la data di ieri (UTC)
        target_date = (datetime.now(timezone.utc).date() - timedelta(days=1)).isoformat()
    try:
        with open('access.log', 'r') as log:
            raw_lines = [l.rstrip('\n') for l in log.readlines() if l.strip()]
            # usa solo le ultime N righe per il polling
            graph_lines = raw_lines[-MAX_GRAPH_LINES:] if len(raw_lines) > MAX_GRAPH_LINES else raw_lines
            if target_date:
                # filtriamo le righe che appartenngono a target_date in base al timestamp all'inizio della riga
                filtered = []
                for line in graph_lines:
                    ts = None
                    parts = line.split(' - ')
                    if parts:
                        ts = parts[0]
                    if not ts:
                        continue
                    # proviamo a parsare timestamp in vari formati
                    parsed = None
                    for fmt in ("%Y-%m-%d %H:%M:%S,%f", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S"):
                        try:
                            parsed = datetime.strptime(ts.strip(), fmt)
                            break
                        except Exception:
                            continue
                    if not parsed:
                        try:
                            parsed = datetime.fromisoformat(ts.strip())
                        except Exception:
                            parsed = None
                    if parsed:
                        # normalizziamo in UTC naive date (parsing potrebbe preservare tzinfo)
                        d = parsed.date()
                        if d.isoformat() == target_date:
                            filtered.append(line)
                # includiamo loopback SEMPRE per il calcolo di ieri (utile in ambiente locale)
                counts = _counts_from_lines_unique_ips(filtered, include_loopback=True)
            else:
                # includiamo loopback SEMPRE anche per il giorno attuale
                counts = _counts_from_lines_unique_ips(graph_lines, include_loopback=True)
    except FileNotFoundError:
        pass
    return jsonify(counts)


# --- Admin endpoints (B)
@bp.route('/antro-1986/security-admin/device-map', methods=['GET'])
def admin_get_device_map():
    # _admin_required()  # Funzione non definita, da implementare se serve protezione admin
    m = _load_device_map()
    return jsonify(m)


@bp.route('/antro-1986/security-admin/rebuild-map', methods=['POST'])
def admin_rebuild_map():
    # _admin_required()  # Funzione non definita, da implementare se serve protezione admin
    try:
        with open('access.log', 'r') as log:
            raw_lines = [l.rstrip('\n') for l in log.readlines() if l.strip()]
        # m = _build_device_map_from_logs(raw_lines, persist=True)  # Funzione non definita
        m = {}  # Placeholder vuoto
        return jsonify({'status': 'ok', 'entries': len(m)})
    except FileNotFoundError:
        return jsonify({'status': 'no_log'})


@bp.route('/antro-1986/security-admin/clear-map', methods=['POST'])
def admin_clear_map():
    # _admin_required()  # Funzione non definita, da implementare se serve protezione admin
    try:
        if DEVICE_MAP_PATH.exists():
            DEVICE_MAP_PATH.unlink()
        return jsonify({'status': 'cleared'})
    except Exception:
        return jsonify({'status': 'error'})


@bp.route('/antro-1986/security-visits')
def security_visits():
    """Endpoint JSON che restituisce serie temporale di visite uniche per giorno dal CSV."""
    labels = []
    data = []
    try:
        with open('visits_history.csv', 'r') as csvfile:
            for line in csvfile:
                line = line.strip()
                if not line or line.startswith('#') or line.lower().startswith('data'):
                    continue
                parts = line.split(',')
                if len(parts) == 2:
                    labels.append(parts[0])
                    try:
                        data.append(int(parts[1]))
                    except ValueError:
                        data.append(0)
    except FileNotFoundError:
        pass
    return jsonify({'labels': labels, 'data': data})
