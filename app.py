from flask import Flask, request, render_template, redirect, url_for, session
import numpy as np
import sqlite3
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a strong secret key

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = sqlite3.connect('matrices.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS operations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operation TEXT NOT NULL,
            matrix1 TEXT NOT NULL,
            matrix2 TEXT,
            result TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def parse_matrix(rows, cols, form, key_prefix='matrix1'):
    matrix = []
    for i in range(rows):
        row = [float(form.get(f'{key_prefix}_{i+1}_{j+1}', 0.0)) for j in range(cols)]
        matrix.append(row)
    return np.array(matrix)

def save_operation_to_db(operation, matrix1, matrix2, result):
    conn = sqlite3.connect('matrices.db')
    c = conn.cursor()
    c.execute("INSERT INTO operations (operation, matrix1, matrix2, result) VALUES (?, ?, ?, ?)",
              (operation, json.dumps(matrix1.tolist()), json.dumps(matrix2.tolist()) if matrix2 is not None else None, json.dumps(result.tolist())))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('matrix_operations'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['username'] = user['username']
            return redirect(url_for('matrix_operations'))
        else:
            return render_template('login.html', message='Invalid username or password.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/matrix_operations')
def matrix_operations():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('matrix_operations.html')

@app.route('/add', methods=['POST'])
def add_matrices():
    rows = int(request.form['rows'])
    cols = int(request.form['cols'])
    matrix1 = parse_matrix(rows, cols, request.form, 'matrix1')
    matrix2 = parse_matrix(rows, cols, request.form, 'matrix2')
    result = matrix1 + matrix2
    save_operation_to_db('Addition', matrix1, matrix2, result)
    return render_template('result.html', operation='Addition', result=result)

@app.route('/subtract', methods=['POST'])
def subtract_matrices():
    rows = int(request.form['rows'])
    cols = int(request.form['cols'])
    matrix1 = parse_matrix(rows, cols, request.form, 'matrix1')
    matrix2 = parse_matrix(rows, cols, request.form, 'matrix2')
    result = matrix1 - matrix2
    save_operation_to_db('Subtraction', matrix1, matrix2, result)
    return render_template('result.html', operation='Subtraction', result=result)

@app.route('/multiply', methods=['POST'])
def multiply_matrices():
    rows1 = int(request.form['rows1'])
    cols1 = int(request.form['cols1'])
    rows2 = int(request.form['rows2'])
    cols2 = int(request.form['cols2'])
    matrix1 = parse_matrix(rows1, cols1, request.form, 'matrix1')
    matrix2 = parse_matrix(rows2, cols2, request.form, 'matrix2')
    if cols1 != rows2:
        return "Matrix dimensions are incompatible for multiplication", 400
    result = np.matmul(matrix1, matrix2)
    save_operation_to_db('Multiplication', matrix1, matrix2, result)
    return render_template('result.html', operation='Multiplication', result=result)

@app.route('/rank', methods=['POST'])
def rank_matrix():
    rows = int(request.form['rows'])
    cols = int(request.form['cols'])
    matrix = parse_matrix(rows, cols, request.form, 'matrix1')
    rank = np.linalg.matrix_rank(matrix)
    save_operation_to_db('Rank', matrix, None, np.array([rank]))
    return render_template('result.html', operation='Rank', rank=rank)

@app.route('/eigen', methods=['POST'])
def compute_eigen():
    rows = int(request.form['rows'])
    cols = int(request.form['cols'])
    if rows != cols:
        return "The matrix must be square to find eigenvalues and eigenvectors.", 400
    matrix = parse_matrix(rows, cols, request.form, 'matrix1')
    eigenvalues, eigenvectors = np.linalg.eig(matrix)
    save_operation_to_db('Eigenvalues and Eigenvectors', matrix, None, eigenvalues)
    return render_template('result.html', operation='Eigenvalues and Eigenvectors', eigenvalues=eigenvalues, eigenvectors=eigenvectors)

@app.route('/admin')
def admin_dashboard():
    if 'username' not in session or session['username'] != 'admin':
        return redirect(url_for('login'))
    conn = sqlite3.connect('matrices.db')
    c = conn.cursor()
    c.execute('SELECT id, username FROM users')
    users = c.fetchall()
    conn.close()
    return render_template('admin_dashboard.html', users=users)

@app.route('/admin/add', methods=['GET', 'POST'])
def add_user():
    if 'username' not in session or session['username'] != 'admin':
        return redirect(url_for('login'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('matrices.db')
        c = conn.cursor()
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_dashboard'))
    return render_template('add_user.html')

@app.route('/admin/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'username' not in session or session['username'] != 'admin':
        return redirect(url_for('login'))
    conn = sqlite3.connect('matrices.db')
    c = conn.cursor()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        c.execute('UPDATE users SET username = ?, password = ? WHERE id = ?', (username, password, user_id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_dashboard'))
    c.execute('SELECT username FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()

    if not user:
        return "User not found", 404
    return render_template('edit_user.html', user=user)

@app.route('/admin/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'username' not in session or session['username'] != 'admin':
        return redirect(url_for('login'))
    conn = sqlite3.connect('matrices.db')
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    init_db()
    app.run(debug=False)
