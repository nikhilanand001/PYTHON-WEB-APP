from flask import Flask, request, render_template
import numpy as np

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def parse_matrix(rows, cols, form, key_prefix='matrix1'):
  matrix = []
  for i in range(rows):
    row = [float(form.get(f'{key_prefix}_{i+1}_{j+1}', 0.0)) for j in range(cols)]
    matrix.append(row)
  return np.array(matrix)


@app.route('/add', methods=['POST'])
def add_matrices():
    rows = int(request.form['rows'])
    cols = int(request.form['cols'])
    matrix1 = parse_matrix(rows, cols, request.form, 'matrix1')
    matrix2 = parse_matrix(rows, cols, request.form, 'matrix2')
    result = matrix1 + matrix2
    return render_template('result.html', operation='Addition', result=result)

@app.route('/subtract', methods=['POST'])
def subtract_matrices():
    rows = int(request.form['rows'])
    cols = int(request.form['cols'])
    matrix1 = parse_matrix(rows, cols, request.form, 'matrix1')
    matrix2 = parse_matrix(rows, cols, request.form, 'matrix2')
    result = matrix1 - matrix2
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
    return render_template('result.html', operation='Multiplication', result=result)

@app.route('/eigen', methods=['POST'])
def compute_eigen():
    rows = int(request.form['rows'])
    cols = int(request.form['cols'])
    if rows!= cols:
        return "The matrix must be square to find eigenvalues and eigenvectors.", 400
    matrix = parse_matrix(rows, cols, request.form, 'matrix1')
    eigenvalues, eigenvectors = np.linalg.eig(matrix)
    return render_template('result.html', operation='Eigenvalues and Eigenvectors', eigenvalues=eigenvalues, eigenvectors=eigenvectors)

if __name__ == '__main__':
    app.run(debug=False)