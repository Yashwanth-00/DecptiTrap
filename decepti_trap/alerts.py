import configparser, smtplib, requests
from email.mime.text import MIMEText

cfg = configparser.ConfigParser()
cfg.read('config.ini')

def send_telegram(message):
    if not cfg.getboolean('telegram','enabled', fallback=False):
        return
    token   = cfg.get('telegram','token')
    chat_id = cfg.get('telegram','chat_id')
    try:
        requests.post(
            f'https://api.telegram.org/bot{token}/sendMessage',
            data={'chat_id': chat_id, 'text': message},
            timeout=5
        )
    except Exception as e:
        print(f'[telegram] error: {e}')

def send_email(subject, body):
    if not cfg.getboolean('email','enabled', fallback=False):
        return
    try:
        msg            = MIMEText(body)
        msg['Subject'] = subject
        msg['From']    = cfg.get('email','smtp_user')
        msg['To']      = cfg.get('email','alert_to')
        with smtplib.SMTP(cfg.get('email','smtp_host'),
                          cfg.getint('email','smtp_port')) as s:
            s.starttls()
            s.login(cfg.get('email','smtp_user'),
                    cfg.get('email','smtp_pass'))
            s.send_message(msg)
    except Exception as e:
        print(f'[email] error: {e}')

def alert(ip, page, reason):
    msg = f'[DeceptiTrap] {reason}\nIP: {ip}\nPage: {page}'
    send_telegram(msg)
    send_email(f'DeceptiTrap Alert — {reason}', msg)
