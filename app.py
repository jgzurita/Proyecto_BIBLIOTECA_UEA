from flask import Flask
app = Flask(__name__)
@app.route('/')
def inicio():
    return "Bienvenido a BIBLIOTECA UEA -- Biblioteca Virtual para consulta de libros"


@app.route('/libro/<LOQUEAGUASELLEVO>')
def libro(LOQUEAGUASELLEVO):
    return f"Libro: {LOQUEAGUASELLEVO} – Consulta cualquie libro en la  BIBLIOTECA UEA."

if __name__ == '__main__':
    app.run(debug=True)
