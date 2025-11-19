import csv
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from services.cloudinary_service import upload_file_to_cloudinary, upload_all_logs_to_cloudinary, download_file_from_cloudinary

VISITS_HISTORY_PATH = Path('visits_history.csv')


def read_visits_history(path: Path = VISITS_HISTORY_PATH):
    history = {}
    if path.exists():
        with open(path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if not row or row[0].startswith('#') or row[0] == 'data':
                    continue
                try:
                    history[row[0]] = int(row[1])
                except Exception:
                    continue
    return history


def append_visit_to_history(date_str, visits, path: Path = VISITS_HISTORY_PATH):
    # Scarica la versione aggiornata prima di modificare
    download_file_from_cloudinary('stats/visits_history.csv', str(path))
    history = read_visits_history(path)
    if date_str in history:
        return
    lines = []
    if path.exists():
        with open(path, encoding='utf-8') as f:
            lines = f.readlines()
    with open(path, 'a', encoding='utf-8') as f:
        if not lines:
            f.write('data,visite\n')
        f.write(f'{date_str},{visits}\n')
    upload_file_to_cloudinary(str(path), folder="stats")
    upload_all_logs_to_cloudinary(log_dir=".", pattern="access.log", folder="logs")


def update_visits_history_from_logs(log_lines, path: Path = VISITS_HISTORY_PATH):
    history = read_visits_history(path)
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    yest_str = yesterday.isoformat()
    if yest_str in history:
        return
    per_day = defaultdict(set)
    for line in log_lines:
        # estraiamo timestamp e ip dall'ultima versione del parser per semplicità
        from services.log_parser import _extract_from_line, _is_bot, _normalize_ip_str
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
        if dt.date() == yesterday:
            per_day[yest_str].add(norm)
    visits = len(per_day[yest_str])
    if visits > 0:
        append_visit_to_history(yest_str, visits, path)


def upload_logs_to_cloudinary():
    try:
        upload_all_logs_to_cloudinary(log_dir='.', pattern='access.log', folder='logs')
    except Exception:
        pass


# Export names compatible with previous code
_read_visits_history = read_visits_history
_append_visit_to_history = append_visit_to_history
_update_visits_history_from_logs = update_visits_history_from_logs
_upload_logs_to_cloudinary = upload_logs_to_cloudinary

