from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/problems')
def problems():
    return render_template('problems.html')

@app.route('/problems/<int:problem_id>')
def problem_detail(problem_id):
    return f"<h2>Details for Problem {problem_id}</h2><p>Here you can add problem description and solution.</p>"

if __name__ == '__main__':
    app.run(debug=True)
