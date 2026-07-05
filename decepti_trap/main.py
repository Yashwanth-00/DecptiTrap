import db
from app import app
import configparser

cfg = configparser.ConfigParser()
cfg.read('config.ini')

if __name__ == '__main__':
    db.init()
    print("""
  ██████╗ ███████╗ ██████╗███████╗██████╗ ████████╗██╗████████╗██████╗  █████╗ ██████╗
  ██╔══██╗██╔════╝██╔════╝██╔════╝██╔══██╗╚══██╔══╝██║╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗
  ██║  ██║█████╗  ██║     █████╗  ██████╔╝   ██║   ██║   ██║   ██████╔╝███████║██████╔╝
  ██║  ██║██╔══╝  ██║     ██╔══╝  ██╔═══╝    ██║   ██║   ██║   ██╔══██╗██╔══██║██╔═══╝
  ██████╔╝███████╗╚██████╗███████╗██║        ██║   ██║   ██║   ██║  ██║██║  ██║██║
  ╚═════╝ ╚══════╝ ╚═════╝╚══════╝╚═╝        ╚═╝   ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝
    """)
    print(f"  [*] honeypot starting...")
    print(f"  [*] lure pages  : / | /admin | /wp-login.php | /.env | /phpmyadmin")
    print(f"  [*] dashboard   : http://localhost:5000/deceptitrap-dashboard")
    print(f"  [*] database    : data/attacks.db")
    print(f"  [*] logs        : logs/deceptitrap.log")
    print(f"  [*] press CTRL+C to stop\n")

    host  = cfg.get('server', 'host',  fallback='0.0.0.0')
    port  = cfg.getint('server', 'port', fallback=5000)
    debug = cfg.getboolean('server', 'debug', fallback=False)
    app.run(host=host, port=port, debug=True)
