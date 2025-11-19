import os
import json
import tempfile
import fcntl
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict

try:
    from services.log_parser import _now_iso, _classify_device_from_ua, _is_bot, _extract_from_line
except Exception:
    from .log_parser import _now_iso, _classify_device_from_ua, _is_bot, _extract_from_line

# Config via env (fallbacks)
MIN_COUNT_TO_SWITCH = int(os.getenv('MIN_COUNT_TO_SWITCH', '3'))
SWITCH_RATIO = float(os.getenv('SWITCH_RATIO', '0.66'))
DEVICE_MAP_PATH = Path('instance') / 'device_map.json'


def _atomic_write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name, text=True)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            except Exception:
                pass
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        # atomic replace
        os.replace(tmp, str(path))
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except Exception:
                pass


def _load_device_map(path: Path = DEVICE_MAP_PATH) -> Dict:
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding='utf-8'))
            first_key = next(iter(data.keys()), None)
            if first_key and isinstance(data[first_key], str):
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


def _save_device_map(m: Dict, path: Path = DEVICE_MAP_PATH):
    try:
        content = json.dumps(m, ensure_ascii=False, indent=2)
        _atomic_write(path, content)
    except Exception:
        pass


def _process_lines_update_map(lines, path: Path = DEVICE_MAP_PATH) -> Dict:
    device_map = _load_device_map(path)
    updated = False
    for line in lines:
        ip, request_path, raw_device, ts = _extract_from_line(line)
        if not ip:
            continue
        if request_path and (request_path.startswith('/antro-1986/security') or request_path.startswith('/static/') or request_path.startswith('/favicon.ico')):
            continue
        if raw_device and _is_bot(raw_device):
            continue
        dev_type = _classify_device_from_ua(raw_device)
        if not dev_type:
            continue
        entry = device_map.get(ip)
        if not entry:
            device_map[ip] = {
                'device': dev_type,
                'counts': {dev_type: 1},
                'first_seen': ts or _now_iso(),
                'last_seen': ts or _now_iso(),
                'last_updated': None
            }
            updated = True
            continue
        counts = entry.get('counts') or {}
        counts[dev_type] = counts.get(dev_type, 0) + 1
        entry['counts'] = counts
        entry['last_seen'] = ts or _now_iso()
        current = entry.get('device')
        if dev_type != current:
            total = sum(counts.values())
            if counts[dev_type] >= MIN_COUNT_TO_SWITCH and counts[dev_type] >= int(SWITCH_RATIO * total):
                entry['device'] = dev_type
                entry['last_updated'] = _now_iso()
                updated = True
    if updated:
        _save_device_map(device_map, path)
    return device_map


# Expose API names compatible with old module
load_device_map = _load_device_map
save_device_map = _save_device_map
process_lines_update_map = _process_lines_update_map

