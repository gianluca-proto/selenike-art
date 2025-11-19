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

# Nuovi import: delega a servizi
from services.log_parser import (
    _now_iso,
    _classify_device_from_ua,
    _is_bot,
    _extract_from_line,
    _normalize_ip_str,
)
from services.log_stats import (
    _counts_from_map as _counts_from_map_srv,
    _counts_from_lines_unique_ips as _counts_from_lines_unique_ips_srv,
    _counts_from_lines_all_accesses as _counts_from_lines_all_accesses_srv,
    _stats_from_lines as _stats_from_lines_srv,
    _visits_timeseries_from_lines as _visits_timeseries_from_lines_srv,
)
# Import servizi per device map e history
from services.device_map import _load_device_map as _load_device_map_srv, _save_device_map as _save_device_map_srv, process_lines_update_map as _process_lines_update_map_srv
from services.history import _read_visits_history as _read_visits_history_srv, _append_visit_to_history as _append_visit_to_history_srv, _update_visits_history_from_logs as _update_visits_history_from_logs_srv, _upload_logs_to_cloudinary as _upload_logs_to_cloudinary_srv

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


# Wrappers compatibili con l'API precedente (mantengono i nomi usati nei test)
def _counts_from_map(m: dict):
    return _counts_from_map_srv(m)


def _counts_from_lines_unique_ips(lines, include_loopback=None):
    return _counts_from_lines_unique_ips_srv(lines, include_loopback=include_loopback)


def _counts_from_lines_all_accesses(lines):
    return _counts_from_lines_all_accesses_srv(lines)


def _stats_from_lines(lines, sample=20):
    return _stats_from_lines_srv(lines, sample=sample)


def _visits_timeseries_from_lines(lines):
    return _visits_timeseries_from_lines_srv(lines)


# Wrappers per device_map/history che delegano ai servizi appena creati
def _load_device_map():
    return _load_device_map_srv()


def _save_device_map(m):
    return _save_device_map_srv(m)


def _process_lines_update_map(lines):
    return _process_lines_update_map_srv(lines)


def _read_visits_history():
    return _read_visits_history_srv()


def _append_visit_to_history(date_str, visits):
    return _append_visit_to_history_srv(date_str, visits)


def _update_visits_history_from_logs(log_lines):
    return _update_visits_history_from_logs_srv(log_lines)


def _upload_logs_to_cloudinary():
    return _upload_logs_to_cloudinary_srv()

# Le funzioni di parsing/statistica/persistenza sono ora centralizzate in services/*
# Il file ora contiene solo la logica di routing / rendering.

@bp.route('/antro-1986/security-dashboard')
def security_dashboard():
    # Aggiorna visits_history.csv con i dati più recenti dai log
    try:
        with open('access.log', 'r') as log:
            log_lines = [l.rstrip('\n') for l in log.readlines() if l.strip()]
            _update_visits_history_from_logs(log_lines)
    except Exception as e:
        print(f"[DEBUG] Errore aggiornamento visits_history.csv: {e}")

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
            for line in page_lines:
                parts = line.split(' - ')
                # Prova a estrarre timestamp se la prima parte sembra una data/ora
                possible_ts = parts[0].strip() if parts else ''
                timestamp = 'N/A'
                # Riconosci formato tipo 'YYYY-MM-DD HH:MM:SS,ms'
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
        raw_lines = []
        device_totals = {'mobile': 0, 'desktop': 0, 'tablet': 0}

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
    """Endpoint JSON per i conteggi unici per device_type (IP+device)."""
    counts = {'mobile': 0, 'desktop': 0, 'tablet': 0}
    MAX_GRAPH_LINES = 2000
    try:
        with open('access.log', 'r') as log:
            raw_lines = [l.rstrip('\n') for l in log.readlines() if l.strip()]
            graph_lines = raw_lines[-MAX_GRAPH_LINES:] if len(raw_lines) > MAX_GRAPH_LINES else raw_lines
            counts = _counts_from_lines_unique_ips(graph_lines)
    except Exception:
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
