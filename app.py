from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import config

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        host=config.DB_HOST,
        database=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASS,
        port=config.DB_PORT
    )
    return conn

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
