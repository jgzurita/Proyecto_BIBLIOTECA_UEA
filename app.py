import os
from flask import Flask, render_template, request, redirect
from models import Producto, Inventario
import database

app = Flask(__name__)

database.crear_tabla()
inventario = Inventario()

@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/libros')
def libros():
    productos = inventario.obtener_todos()
    return render_template('libros.html', productos=productos)





@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        nombre = request.form['nombre']
        cantidad = request.form['cantidad']
        precio = request.form['precio']

        if not nombre:
            return "El nombre es obligatorio", 400

        producto = Producto(None, nombre, cantidad, precio)
        inventario.agregar(producto)
        return redirect('/libros')

    return render_template('agregar.html')




@app.route('/eliminar/<int:id>')
def eliminar(id):
    inventario.eliminar(id)
    return redirect('/libros')




if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)