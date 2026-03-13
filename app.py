import os
from flask import Flask, render_template, request, redirect
from conexion.conexion import obtener_conexion



app = Flask(__name__)



# pagina principal
@app.route('/')
def inicio():
    return render_template('index.html')

# pagina acerca de
@app.route('/about')
def about():
    return render_template('about.html')



# mostrar inventario de libros
@app.route('/libros')
def libros():

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM libros")

    libros = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template('libros.html', libros=libros)




# agregar libro
@app.route('/agregar', methods=['GET','POST'])
def agregar():

    if request.method == 'POST':

        nombre = request.form['nombre']
        categoria = request.form['categoria']
        descripcion = request.form['descripcion']
        autor = request.form['autor']
        editorial = request.form['editorial']
        cantidad = request.form['cantidad']

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        sql = """
        INSERT INTO libros(nombre,categoria,descripcion,autor,editorial,cantidad)
        VALUES(%s,%s,%s,%s,%s,%s)
        """

        cursor.execute(sql,(nombre,categoria,descripcion,autor,editorial,cantidad))

        conexion.commit()

        cursor.close()
        conexion.close()

        return redirect('/libros')

    return render_template('agregar.html')





# eliminar libro
@app.route('/eliminar/<int:id>')
def eliminar(id):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("DELETE FROM libros WHERE id_libro=%s",(id,))

    conexion.commit()

    cursor.close()
    conexion.close()

    return redirect('/libros')

# iniciar servidor
if __name__ == '__main__':
    port = int(os.environ.get("PORT",5000))
    app.run(host='0.0.0.0',port=port)