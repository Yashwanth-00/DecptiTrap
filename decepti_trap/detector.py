from collections import defaultdict
from datetime import datetime, timedelta
import configparser
import alerts

cfg = configparser.ConfigParser()
cfg.read('config.ini')

THRESHOLD = cfg.getint('detection', 'brute_force_threshold', fallback=5)
WINDOW    = cfg.getint('detection', 'scan_window_seconds',   fallback=60)

# ip -> list of timestamps
_hits = defaultdict(list)

def check(ip, page):
    now = datetime.now()
    _hits[ip].append(now)
    # drop old entries outside window
    _hits[ip] = [t for t in _hits[ip] if now - t < timedelta(seconds=WINDOW)]
    count = len(_hits[ip])
    if count == THRESHOLD:
        alerts.alert(ip, page, f'Brute force detected — {count} hits in {WINDOW}s')
    return count
