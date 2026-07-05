# DeceptiTrap 🪤
A lightweight honeypot that simulates a vulnerable web server,
logs every attacker/scanner that probes it, and shows everything
on a live dashboard.

---

## File Structure

```
deceptitrap/
├── main.py              ← run this to start everything
├── app.py               ← flask routes (all the lure pages + API)
├── db.py                ← sqlite setup + read/write functions
├── detector.py          ← brute force detection logic
├── alerts.py            ← telegram / email notifications
├── config.ini           ← all settings in one place
├── requirements.txt
├── templates/
│   ├── index.html       ← fake Apache default page (the bait)
│   ├── admin.html       ← fake admin login panel
│   ├── wp_login.html    ← fake WordPress login
│   ├── phpmyadmin.html  ← fake phpMyAdmin
│   ├── 404.html         ← fake Apache 404
│   └── dashboard.html   ← YOUR real monitoring dashboard
├── data/
│   └── attacks.db       ← auto-created sqlite database
└── logs/
    └── deceptitrap.log  ← raw text backup log
```

---

## What Gets Captured

Every time someone visits any page, the system logs:
- IP address
- Page they hit  ( /.env  /admin  /wp-login.php  etc )
- HTTP method (GET / POST)
- User-Agent (tells you if it's a scanner bot or a browser)
- Referrer
- Extra note (LOGIN_ATTEMPT, ENV_PROBE, WEBSHELL_PROBE etc)
- Timestamp

All stored in SQLite → visible on your dashboard.

---

## Setup & Run

### 1. Install dependencies
```bash
cd deceptitrap
pip install -r requirements.txt
```

### 2. Start the honeypot
```bash
python main.py
```

### 3. Open your dashboard
```
http://localhost:5000/deceptitrap-dashboard
```

### 4. Lure pages (what attackers see)
```
http://localhost:5000/              → fake Apache default page
http://localhost:5000/admin         → fake admin login
http://localhost:5000/wp-login.php  → fake WordPress login
http://localhost:5000/.env          → fake environment file
http://localhost:5000/phpmyadmin    → fake phpMyAdmin
http://localhost:5000/shell.php     → 404 (but gets logged)
```
Any unknown URL also gets logged via the 404 handler.

---

## Enable Telegram Alerts

1. Message @BotFather on Telegram → create a bot → copy the token
2. Message your bot once, then visit:
   https://api.telegram.org/bot<TOKEN>/getUpdates
   Copy your chat_id from the response
3. Edit config.ini:
```ini
[telegram]
enabled = true
token   = 123456:ABCdef...
chat_id = 987654321
```
Restart → you'll get a Telegram message every time
the brute-force threshold is hit.

---

## Enable Email Alerts

1. Use a Gmail account
2. Go to Google Account → Security → App Passwords → generate one
3. Edit config.ini:
```ini
[email]
enabled   = true
smtp_host = smtp.gmail.com
smtp_port = 587
smtp_user = you@gmail.com
smtp_pass = your_16char_app_password
alert_to  = you@gmail.com
```

---

## Tune Detection Thresholds

In config.ini:
```ini
[detection]
brute_force_threshold = 5    ← hits from same IP before alert fires
scan_window_seconds   = 60   ← time window to count those hits in
```

---

## View Raw Database

```bash
sqlite3 data/attacks.db
sqlite> SELECT * FROM attacks ORDER BY id DESC LIMIT 20;
sqlite> SELECT ip, COUNT(*) as hits FROM attacks GROUP BY ip ORDER BY hits DESC;
sqlite> SELECT page, COUNT(*) as hits FROM attacks GROUP BY page ORDER BY hits DESC;
sqlite> .quit
```

---

## Deploy on a VPS (optional — to catch real scanners)

If you want to expose this to the real internet:

1. Get a cheap VPS (DigitalOcean, Vultr, Linode — $5/mo)
2. SSH in, clone your repo, install requirements
3. Run on port 80 (needs sudo or port forwarding):
```bash
sudo python main.py    # edit config.ini port to 80 first
```
Or use a proper setup:
```bash
pip install gunicorn
sudo gunicorn -w 2 -b 0.0.0.0:80 app:app
```
4. Within hours automated scanners will hit /.env, /wp-login.php etc
   and you'll see real attacker data in your dashboard.

NOTE: Never deploy this on a network you don't own.
Only on your own VPS or local machine.

---

## Adding Cowrie (SSH Honeypot)

Cowrie captures SSH brute force attempts on port 22.
It logs everything to JSON which you can import into your db.

```bash
# install cowrie (separate from this project)
sudo apt install python3-venv libssl-dev libffi-dev build-essential
git clone https://github.com/cowrie/cowrie
cd cowrie
python3 -m venv cowrie-env
source cowrie-env/bin/activate
pip install -r requirements.txt
cp etc/cowrie.cfg.dist etc/cowrie.cfg
bin/cowrie start
```

Cowrie logs land in cowrie/var/log/cowrie/cowrie.json
You can write a small script to tail that file and insert
rows into your attacks.db using db.log_attack().

---

## API Endpoints

These are used by the dashboard — you can also hit them directly:

GET /api/attacks      → last 300 attack rows as JSON
GET /api/stats        → totals, top IP, top page, page breakdown

---

## Tech Stack

| thing         | what it does                        |
|---------------|-------------------------------------|
| Flask         | web framework — serves lure pages + dashboard |
| SQLite        | stores every hit, zero config needed |
| Fira Code     | monospace font in the dashboard     |
| Vanilla JS    | dashboard polls /api/attacks every 4s |
| configparser  | reads config.ini                    |
| requests      | sends Telegram alerts               |
| smtplib       | sends email alerts                  |

---

## What Attackers / Bots Actually Do

When you expose this to the internet, automated tools constantly:
- Scan for /.env to steal API keys and DB passwords
- Brute force /admin and /wp-login.php with wordlists
- Probe /phpmyadmin to get database access
- Try /shell.php /cmd.php looking for existing webshells
- Hit random paths looking for known CVEs

All of this gets captured. That's the point.

---

## Troubleshooting

Port already in use:
  Change port in config.ini or kill the process using that port:
  lsof -i :5000   then   kill -9 <PID>

Module not found:
  pip install -r requirements.txt

Database locked:
  Only run one instance of main.py at a time.

Dashboard shows no data:
  Visit http://localhost:5000/admin first to generate a hit,
  then refresh the dashboard.
