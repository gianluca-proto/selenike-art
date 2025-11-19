from collections import defaultdict
from datetime import datetime

from services.log_parser import (
    _extract_from_line,
    _classify_device_from_ua,
    _is_bot,
    _normalize_ip_str,
)


def _parse_ts(ts):
    if not ts:
        return None
    if isinstance(ts, datetime):
        return ts
    s = str(ts).strip()
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            if s.endswith('Z') and '%z' not in fmt:
                return datetime.strptime(s, fmt)
            return datetime.strptime(s, fmt)
        except Exception:
            continue
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


def _counts_from_map(m: dict):
    """Dalla mappa persistente ritorna conteggi per device scegliendo l'entry con last_seen più recente per IP normalizzato."""
    if not isinstance(m, dict):
        return {'mobile': 0, 'desktop': 0, 'tablet': 0}

    grouped = {}
    for raw_key, entry in (m.items() if isinstance(m, dict) else []):
        norm = _normalize_ip_str(raw_key)
        if not norm:
            continue
        cur = grouped.get(norm)
        cur_ts = _parse_ts(cur.get('last_seen')) if cur else None
        ent_ts = _parse_ts(entry.get('last_seen'))
        take = False
        if cur is None:
            take = True
        else:
            if ent_ts and cur_ts:
                if ent_ts > cur_ts:
                    take = True
            elif ent_ts and not cur_ts:
                take = True
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


def _counts_from_lines_unique_ips(lines, include_loopback=None, include_func=None):
    """Conta una entry per combinazione IP+device.

    include_loopback: se None usa valore default False
    include_func: funzione opzionale per includere linee aggiuntive (non usata normalmente)
    """
    seen = set()
    device_counts = {'mobile': 0, 'desktop': 0, 'tablet': 0}
    use_loopback = False
    if include_loopback is not None:
        use_loopback = bool(include_loopback)

    for line in lines:
        ip, request_path, raw_device, ts = _extract_from_line(line)
        if not ip:
            continue
        if request_path and (request_path.startswith('/antro-1986/security') or request_path.startswith('/static/') or request_path.startswith('/favicon.ico')):
            continue
        if raw_device and _is_bot(raw_device):
            continue
        norm = _normalize_ip_str(ip)
        if not norm:
            continue
        if not use_loopback:
            try:
                nip = __import__('ipaddress').ip_address(norm)
                if nip.is_loopback:
                    continue
            except Exception:
                if norm in ('127.0.0.1', '::1'):
                    continue
        dev_type = _classify_device_from_ua(raw_device)
        if not dev_type:
            dev_type = 'desktop'
        key = (norm, dev_type)
        if key in seen:
            continue
        seen.add(key)
        if dev_type in device_counts:
            device_counts[dev_type] += 1
        else:
            device_counts['desktop'] += 1
    return device_counts


def _counts_from_lines_all_accesses(lines):
    device_counts = {'mobile': 0, 'desktop': 0, 'tablet': 0}
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
            dev_type = 'desktop'
        if dev_type in device_counts:
            device_counts[dev_type] += 1
        else:
            device_counts['desktop'] += 1
    return device_counts


def _stats_from_lines(lines, sample=20):
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
        dev_type = _classify_device_from_ua(raw_device)
        if not dev_type:
            excluded += 1
            continue
        key = f"{norm}|{dev_type}"
        if key in seen:
            continue
        seen[key] = {'device': dev_type, 'raw_ua': raw_device, 'request': request_path, 'ts': ts, 'ip': norm}

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
        'unique_ip_device': len(seen),
        'total_lines': total,
        'excluded_lines': excluded,
        'sample_seen': sample_items
    }


def _visits_timeseries_from_lines(lines):
    per_day = defaultdict(set)
    for line in lines:
        ip, request_path, raw_device, ts = _extract_from_line(line)
        if not ip:
            continue
        if request_path and (request_path.startswith('/antro-1986/security') or request_path.startswith('/static/') or request_path.startswith('/favicon.ico')):
            continue
        if raw_device and _is_bot(raw_device):
            continue
        norm = _normalize_ip_str(ip)
        if not norm:
            continue
        try:
            nip = __import__('ipaddress').ip_address(norm)
            if nip.is_loopback:
                continue
        except Exception:
            if norm in ('127.0.0.1', '::1'):
                continue
        if not ts:
            continue
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
