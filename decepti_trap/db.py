import sqlite3, os
from datetime import datetime

DB_PATH = 'data/attacks.db'

def init():
    os.makedirs('data', exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.execute('''CREATE TABLE IF NOT EXISTS attacks (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        ip        TEXT,
        page      TEXT,
        method    TEXT,
        user_agent TEXT,
        referrer  TEXT,
        extra     TEXT,
        timestamp TEXT
    )''')
    con.commit()
    con.close()

def log_attack(ip, page, method, user_agent, referrer, extra):
    con = sqlite3.connect(DB_PATH)
    con.execute('INSERT INTO attacks VALUES (NULL,?,?,?,?,?,?,?)',
                (ip, page, method, user_agent, referrer, extra,
                 datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    con.commit()
    con.close()

def get_attacks(limit=300):
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    rows = con.execute('SELECT * FROM attacks ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
    con.close()
    return [dict(r) for r in rows]

def get_stats():
    con = sqlite3.connect(DB_PATH)
    total     = con.execute('SELECT COUNT(*) FROM attacks').fetchone()[0]
    unique_ip = con.execute('SELECT COUNT(DISTINCT ip) FROM attacks').fetchone()[0]
    top_page  = con.execute('SELECT page, COUNT(*) as c FROM attacks GROUP BY page ORDER BY c DESC LIMIT 1').fetchone()
    top_ip    = con.execute('SELECT ip, COUNT(*) as c FROM attacks GROUP BY ip ORDER BY c DESC LIMIT 1').fetchone()
    by_page   = con.execute('SELECT page, COUNT(*) as c FROM attacks GROUP BY page ORDER BY c DESC').fetchall()
    con.close()
    return {
        'total':     total,
        'unique_ip': unique_ip,
        'top_page':  {'page': top_page[0], 'c': top_page[1]} if top_page else {},
        'top_ip':    {'ip':   top_ip[0],   'c': top_ip[1]}   if top_ip   else {},
        'by_page':   [{'page': r[0], 'c': r[1]} for r in by_page],
    }
