from flask import Flask, request, render_template
import numpy as np
import sqlite3
import json

app = Flask(__name__)

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
    return render_template('index.html')

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

if __name__ == '__main__':
    app.run(debug=True)
