from flask import Flask, request, render_template, jsonify
import db, logging, os

app = Flask(__name__)
os.makedirs('logs', exist_ok=True)
logging.basicConfig(filename='logs/deceptitrap.log', level=logging.INFO,
                    format='%(asctime)s %(message)s')

def log_hit(page, extra=""):
    ip       = request.headers.get('X-Forwarded-For', request.remote_addr)
    ua       = request.headers.get('User-Agent', '')
    referrer = request.referrer or ''
    db.log_attack(ip=ip, page=page, method=request.method,
                  user_agent=ua, referrer=referrer, extra=extra)
    logging.info(f"{ip} {request.method} {page} | {ua}")

@app.route('/')
def index():
    log_hit('/')
    return render_template('index.html')

@app.route('/admin', methods=['GET','POST'])
@app.route('/admin/', methods=['GET','POST'])
def admin():
    error = None
    if request.method == 'POST':
        log_hit('/admin', extra="LOGIN_ATTEMPT")
        error = "Invalid credentials."
    else:
        log_hit('/admin')
    return render_template('admin.html', error=error)

@app.route('/wp-login.php', methods=['GET','POST'])
def wp_login():
    if request.method == 'POST':
        log_hit('/wp-login.php', extra="WP_LOGIN_ATTEMPT")
        return render_template('wp_login.html', error="ERROR: Cookies are blocked.")
    log_hit('/wp-login.php')
    return render_template('wp_login.html', error=None)

@app.route('/.env')
def env_file():
    log_hit('/.env', extra="ENV_PROBE")
    return app.response_class(
        response="APP_KEY=base64:fakekey==\nDB_PASSWORD=fake\nAWS_SECRET=FAKE\n",
        mimetype='text/plain')

@app.route('/phpmyadmin', methods=['GET','POST'])
@app.route('/phpmyadmin/', methods=['GET','POST'])
def phpmyadmin():
    log_hit('/phpmyadmin', extra="PMA_PROBE" if request.method=='POST' else "")
    return render_template('phpmyadmin.html', error="Cannot connect to MySQL server")

@app.route('/shell.php')
@app.route('/cmd.php')
def shell():
    log_hit(request.path, extra="WEBSHELL_PROBE")
    return "404 Not Found", 404

@app.errorhandler(404)
def not_found(e):
    log_hit(request.path, extra="404_PROBE")
    return render_template('404.html'), 404

# dashboard
@app.route('/deceptitrap-dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/attacks')
def api_attacks():
    return jsonify(db.get_attacks(limit=300))

@app.route('/api/stats')
def api_stats():
    return jsonify(db.get_stats())

if __name__ == '__main__':
    db.init()
    app.run(host='0.0.0.0', port=5000, debug=False)
