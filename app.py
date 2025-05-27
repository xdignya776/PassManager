from flask import Flask, request, redirect, url_for, session
from markupsafe import escape, Markup
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
import threading
import webview

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_KEY')
DB_PATH = ('.data/.unknown')
MAX_USERS = 10

def make_dir_and_init_db():
    os.makedirs('.data', exist_ok=True)
    if not os.path.exists(DB_PATH):
        init_db()
        os.chmod(DB_PATH, 0o600)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL )
    ''')
    db.execute('''
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            service TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    db.commit()
    db.close()


def get_user(username):
    db = get_db()
    cur = db.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cur.fetchone()
    db.close()
    return user

def get_user_by_id(user_id):
    db = get_db()
    cur = db.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cur.fetchone()
    db.close()
    return user

def user_count():
    db = get_db()
    cur = db.execute('SELECT COUNT(*) as cnt FROM users')
    cnt = cur.fetchone()['cnt']
    db.close()
    return cnt

def create_user(username, password):
    db = get_db()
    password_hash = generate_password_hash(password)
    db.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
    db.commit()
    db.close()
    return password_hash

def verify_user(username, password):
    user = get_user(username)
    if user and check_password_hash(user['password_hash'], password):
        return user
    return None

def get_all_passwords(user_id):
    db = get_db()
    cur = db.execute('SELECT id, service, username, password FROM passwords WHERE user_id = ?', (user_id,))
    rows = cur.fetchall()
    db.close()
    return rows

def add_password(user_id, service, username, password):
    db = get_db()
    db.execute('INSERT INTO passwords (user_id, service, username, password) VALUES (?, ?, ?, ?)', (user_id, service, username, password))
    db.commit()
    db.close()

def delete_password(user_id, row_id):
    db = get_db()
    db.execute('DELETE FROM passwords WHERE id = ? AND user_id = ?', (row_id, user_id))
    db.commit()
    db.close()

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ""
    if user_count() >= MAX_USERS:
        msg = "<div style='color:red'>Maximum number of users reached.</div>"
        return Markup(f"""
            <h2>Register</h2>
            {msg}
            <a href='/login'>Login</a>
        """)
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if not username or not password:
            msg = "<div style='color:red'>All fields required.</div>"
        elif get_user(username):
            msg = "<div style='color:red'>Username already exists.</div>"
        else:
            create_user(username, password)
            msg = "<div style='color:green'>Registration successful! You can now <a href='/login'>login</a>.</div>"
    return Markup(f"""
        <h2>Register</h2>
        {msg}
        <form method='post'>
            <input name='username' placeholder='Username'>
            <input name='password' placeholder='Password' type='password'>
            <button type='submit'>Register</button>
        </form>
        <a href='/login'>Login</a>
    """)
    return Markup(f"""
        <h2>Register</h2>
        {msg}
        <form method='post'>
            <input name='username' placeholder='Username'>
            <input name='password' placeholder='Password' type='password'>
            <button type='submit'>Register</button>
        </form>
        <a href='/login'>Login</a>
    """)

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user = verify_user(username, password)
        if not user:
            msg = "<div style='color:red'>Invalid username or password.</div>"
        else:
                session['logged_in'] = True
                session['user_id'] = user['id']
                session['username'] = username
                return redirect(url_for('index'))
    return Markup(f"""
        <h2>Login</h2>
        {msg}
        <form method='post'>
            <input name='username' placeholder='Username'>
            <input name='password' placeholder='Password' type='password'>
            <button type='submit'>Login</button>
        </form>
        <a href='/register'>Register</a>
    """)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/", methods=["GET", "POST"])
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    msg = ""
    user_id = session['user_id']
    if request.method == "POST":
        if "add" in request.form:
            service = request.form.get("service", "").strip()
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "").strip()
            if service and username and password:
                add_password(user_id, service, username, password)
                msg = "<div style='color:green'>Password added!</div>"
            else:
                msg = "<div style='color:red'>All fields required.</div>"
        elif "delete" in request.form:
            row_id = int(request.form.get("delete"))
            delete_password(user_id, row_id)
            msg = "<div style='color:orange'>Password deleted.</div>"

    passwords = get_all_passwords(user_id)
    html = f"""
    <html>
    <head>
        <title>Password Manager</title>
    </head>
    <body>
        <h2>Password Manager</h2>
        <div>Logged in as: <b>{escape(session['username'])}</b> | <a href='/logout'>Logout</a></div>
        {msg}
        <form method='post'>
            <input name='service' placeholder='Service'>
            <input name='username' placeholder='Username'>
            <input name='password' placeholder='Password' type='password'>
            <button type='submit' name='add'>Add Pass</button>
        </form>
        <h3>Saved Passwords</h3>
        <table border='1' cellpadding='5'>
            <tr><th>ID</th><th>Service</th><th>Username</th><th>Password</th><th>Action</th></tr>
            {''.join(f"<tr><td>{p['id']}</td><td>{escape(p['service'])}</td><td>{escape(p['username'])}</td><td>{escape(p['password'])}</td>"
                    f"<td><form method='post' style='display:inline'><button name='delete' value='{p['id']}'>Delete</button></form></td></tr>" for p in passwords)}
        </table>
    </body>
    </html>
    """
    return Markup(html)

def start_flask():
    make_dir_and_init_db()
    app.run(port=9090, debug=False, use_reloader=False)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()

    webview.create_window("Password Manager", "http://127.0.0.1:9090/")
    webview.start()