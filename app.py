from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import config

from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import User
import psycopg2.extras
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

app.secret_key = 'f1c2d3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4'  # change this in production

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user_row = cur.fetchone()
    cur.close()
    conn.close()
    if user_row:
        return User(user_row['id'], user_row['username'], user_row['password'], user_row['role'])
    return None


def get_db_connection():
    conn = psycopg2.connect(
        host=config.DB_HOST,
        database=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASS,
        port=config.DB_PORT
    )
    return conn

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('SELECT * FROM users WHERE username = %s', (username,))
        user_row = cur.fetchone()
        cur.close()
        conn.close()

        if user_row and check_password_hash(user_row['password'], password):
            user = User(user_row['id'], user_row['username'], user_row['password'], user_row['role'])
            login_user(user)
            return redirect(url_for('home'))
        else:
            return 'Invalid credentials'

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/problems')
def problems():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, title FROM problems;')
    problems = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('problems.html', problems=problems)

@app.route('/problems/<int:problem_id>')
def problem_detail(problem_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT title, description FROM problems WHERE id = %s;', (problem_id,))
    problem = cur.fetchone()
    cur.close()
    conn.close()
    if problem:
        return render_template('problem_detail.html', problem=problem)
    else:
        return f"<h2>No problem found with ID {problem_id}</h2>"

# 👇 Add this new route here
@app.route('/add', methods=['GET', 'POST'])
def add_problem():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO problems (title, description) VALUES (%s, %s)', (title, description))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('problems'))
    return render_template('add_problem.html')

@app.route('/test-db')
def test_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM problems;')
    result = cur.fetchall()
    cur.close()
    conn.close()
    return f"<pre>{result}</pre>"

@app.route('/delete/<int:problem_id>', methods=['POST'])
def delete_problem(problem_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM problems WHERE id = %s;', (problem_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('problems'))





if __name__ == '__main__':
    app.run(debug=True, port=5001)
