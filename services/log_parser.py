# servizi per parsing delle righe di log e normalizzazione IP
import re
import ipaddress
from datetime import datetime, timezone

try:
    from user_agents import parse as ua_parse
except Exception:
    ua_parse = None


def _now_iso():
    """Timestamp ISO 8601 UTC timezone-aware"""
    return datetime.now(timezone.utc).isoformat()


def _classify_device_from_ua(ua_string):
    """Classifica in desktop/mobile/tablet usando user-agents se disponibile, altrimenti heuristica semplice.
    Ritorna None se ua_string è mancante o non valida.
    """
    if not ua_string:
        return None
    s = ua_string.lower()
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
        if ip.startswith('[') and ']' in ip:
            inner = ip.split(']', 1)[0][1:]
            ip = inner
        else:
            mport = re.match(r'^(.*?):(\d+)$', ip)
            if mport:
                ip = mport.group(1)
    try:
        if len(parts) > 3 and 'Request:' in parts[3]:
            raw_req = parts[3].split('Request: ', 1)[1].strip()
            if ' ' in raw_req:
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
        if len(possible) > 20:
            ua_indicators = ['mozilla', 'curl', 'android', 'iphone', 'mobile', 'safari', 'chrome', 'edg', 'firefox']
            s_low = possible.lower()
            if any(ind in s_low for ind in ua_indicators):
                raw_device = possible
            else:
                raw_device = None
    return ip, request_path, raw_device, ts


def _normalize_ip_str(ip_str):
    """Normalizza e valida una stringa IP; ritorna la forma canonica (str) o None se non valida."""
    if not ip_str:
        return None
    s = str(ip_str).strip()
    if s.startswith('[') and ']' in s:
        inner = s.split(']', 1)[0][1:]
        s = inner
    if '.' in s:
        if ':' in s:
            head, tail = s.rsplit(':', 1)
            if tail.isdigit():
                s = head
        try:
            ip = ipaddress.ip_address(s)
            return str(ip)
        except Exception:
            if re.search(r"\d", s) and '.' in s:
                return s
            return None
    try:
        ip = ipaddress.ip_address(s)
        return str(ip)
    except Exception:
        if re.search(r"\d", s) and ':' in s:
            return s
        return None

