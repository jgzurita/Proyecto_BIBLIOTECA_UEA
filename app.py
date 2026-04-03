import os
from flask import Flask, render_template, request, redirect, url_for, send_file
from conexion.conexion import obtener_conexion
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import io
from werkzeug.security import generate_password_hash


import re



app = Flask(__name__)
app.secret_key = "clave_secreta"

# login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# imagenes
UPLOAD_FOLDER = 'static/img/libros'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# modelo usuario
class Usuario(UserMixin):
    def __init__(self, id, nombre, email, password, tipo):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.password = password
        self.tipo = tipo

    def get_id(self):
        return f"{self.tipo}-{self.id}"

# cargar usuario
@login_manager.user_loader
def load_user(user_id):
    try:
        tipo, id_real = user_id.split("-")
    except:
        return None

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    if tipo == "usuario":
        cursor.execute("SELECT * FROM usuarios WHERE id_usuario=%s", (id_real,))
        user = cursor.fetchone()
        if user:
            return Usuario(user['id_usuario'], user['nombre'], user['email'], user['password'], "usuario")

    elif tipo == "admin":
        cursor.execute("SELECT * FROM administradores WHERE id_admin=%s", (id_real,))
        admin = cursor.fetchone()
        if admin:
            return Usuario(admin['id_admin'], admin['nombre'], admin['email'], admin['password'], "admin")

    cursor.close()
    conexion.close()
    return None

# inicio
@app.route('/')
def inicio():
    return redirect(url_for('login'))

# about
@app.route('/about')
@login_required
def about():
    return render_template('about.html')

# libros
@app.route('/libros')
@login_required
def libros():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM libros WHERE estado = 1 OR estado IS NULL")
    libros = cursor.fetchall()

    cursor.execute("""
    SELECT p.id_prestamo, l.nombre, u.nombre AS usuario, p.fecha_prestamo
    FROM prestamos p
    JOIN libros l ON p.id_libro = l.id_libro
    JOIN usuarios u ON p.id_usuario = u.id_usuario
    WHERE p.estado = 'prestado'
    """)
    prestamos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template('libros.html', libros=libros, prestamos=prestamos)

# agregar
@app.route('/agregar', methods=['GET','POST'])
@login_required
def agregar():

    if current_user.tipo != "admin":
        return "acceso denegado", 403

    if request.method == 'POST':
        nombre = request.form['nombre']
        categoria = request.form['categoria']
        descripcion = request.form['descripcion']
        autor = request.form['autor']
        editorial = request.form['editorial']
        cantidad = request.form['cantidad']

        imagen = request.files['imagen']
        nombre_imagen = None

        if imagen and imagen.filename != "":
            nombre_imagen = secure_filename(imagen.filename)
            ruta = os.path.join(app.config['UPLOAD_FOLDER'], nombre_imagen)
            imagen.save(ruta)

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
        INSERT INTO libros(nombre,categoria,descripcion,autor,editorial,cantidad,imagen,estado)
        VALUES(%s,%s,%s,%s,%s,%s,%s,1)
        """,(nombre,categoria,descripcion,autor,editorial,cantidad,nombre_imagen))

        conexion.commit()
        cursor.close()
        conexion.close()

        return redirect(url_for('libros'))

    return render_template('agregar.html')

# eliminar logico
@app.route('/eliminar/<int:id>')
@login_required
def eliminar(id):

    if current_user.tipo != "admin":
        return "acceso denegado", 403

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("UPDATE libros SET estado=0 WHERE id_libro=%s",(id,))
    conexion.commit()

    cursor.close()
    conexion.close()

    return redirect(url_for('libros'))

# editar
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):

    if current_user.tipo != "admin":
        return "acceso denegado", 403

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM libros WHERE id_libro=%s", (id,))
    libro = cursor.fetchone()

    if request.method == 'POST':
        nombre = request.form['nombre']
        categoria = request.form['categoria']
        descripcion = request.form['descripcion']
        autor = request.form['autor']
        editorial = request.form['editorial']
        cantidad = request.form['cantidad']

        cursor.execute("""
        UPDATE libros 
        SET nombre=%s, categoria=%s, descripcion=%s, autor=%s, editorial=%s, cantidad=%s
        WHERE id_libro=%s
        """, (nombre, categoria, descripcion, autor, editorial, cantidad, id))

        conexion.commit()
        cursor.close()
        conexion.close()

        return redirect(url_for('libros'))

    cursor.close()
    conexion.close()
    return render_template('editar.html', libro=libro)

# registro
@app.route('/registro', methods=['GET','POST'])
def registro():

    errores = {}

    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        telefono = request.form['telefono']
        password = request.form['password']

        # validar nombre (solo letras)
        if not nombre.replace(" ", "").isalpha():
            errores['nombre'] = "solo se permiten letras"

        # validar telefono (10 numeros exactos)
        if not telefono.isdigit() or len(telefono) != 10:
            errores['telefono'] = "debe tener exactamente 10 numeros"

        # validar contraseña segura
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).+$', password):
            errores['password'] = "debe tener mayuscula, minuscula, numero y caracter especial"

        # validar correo simple
        if "@" not in email:
            errores['email'] = "correo invalido"

        # si hay errores → NO guarda, solo muestra
        if errores:
            return render_template(
                'registro.html',
                errores=errores,
                datos=request.form
            )

        # guardar normal
        password_hash = generate_password_hash(password)

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            "INSERT INTO usuarios(nombre,email,telefono,password) VALUES(%s,%s,%s,%s)",
            (nombre,email,telefono,password_hash)
        )

        conexion.commit()
        cursor.close()
        conexion.close()

        return redirect(url_for('login'))

    return render_template('registro.html', errores={}, datos={})
# login corregido
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        # usuarios (con hash)
        cursor.execute("SELECT * FROM usuarios WHERE email=%s", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            usuario = Usuario(
                user['id_usuario'],
                user['nombre'],
                user['email'],
                user['password'],
                "usuario"
            )
            login_user(usuario)

            cursor.close()
            conexion.close()
            return redirect(url_for('libros'))

        # admin (hash o texto plano)
        cursor.execute("SELECT * FROM administradores WHERE email=%s", (email,))
        admin = cursor.fetchone()

        if admin:
            password_db = admin['password']

            # 🔥 acepta hash o texto plano
            if check_password_hash(password_db, password) or password_db == password:
                usuario = Usuario(
                    admin['id_admin'],
                    admin['nombre'],
                    admin['email'],
                    admin['password'],
                    "admin"
                )
                login_user(usuario)

                cursor.close()
                conexion.close()
                return redirect(url_for('libros'))

        cursor.close()
        conexion.close()

        return render_template('login.html', error="credenciales incorrectas")

    return render_template('login.html')
# logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))



# prestar libro
@app.route('/prestar/<int:id>', methods=['GET', 'POST'])
@login_required
def prestar(id):

    if current_user.tipo != "admin":
        return "acceso denegado", 403

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM libros WHERE id_libro=%s", (id,))
    libro = cursor.fetchone()

    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()

    if request.method == 'POST':
        id_usuario = request.form['usuario']
        id_admin = current_user.id

        if libro['cantidad'] <= 0:
            return "no hay stock disponible"

        cursor.execute("""
        INSERT INTO prestamos(id_libro, id_usuario, id_admin, fecha_prestamo, estado)
        VALUES(%s,%s,%s,NOW(),'prestado')
        """, (id, id_usuario, id_admin))

        cursor.execute("""
        UPDATE libros SET cantidad = cantidad - 1
        WHERE id_libro=%s
        """, (id,))

        conexion.commit()

        cursor.close()
        conexion.close()

        return redirect(url_for('libros'))

    cursor.close()
    conexion.close()

    return render_template('prestar.html', libro=libro, usuarios=usuarios)





#########
# devolver libro
@app.route('/devolver/<int:id>')
@login_required
def devolver(id):

    if current_user.tipo != "admin":
        return "acceso denegado", 403

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # obtener libro del prestamo
    cursor.execute("SELECT id_libro FROM prestamos WHERE id_prestamo=%s", (id,))
    prestamo = cursor.fetchone()

    if prestamo:
        id_libro = prestamo[0]

        # actualizar prestamo
        cursor.execute("""
        UPDATE prestamos 
        SET estado='devuelto', fecha_devolucion=NOW()
        WHERE id_prestamo=%s
        """, (id,))

        # devolver stock
        cursor.execute("""
        UPDATE libros SET cantidad = cantidad + 1
        WHERE id_libro=%s
        """, (id_libro,))

        conexion.commit()

    cursor.close()
    conexion.close()

    return redirect(url_for('libros'))





########


# reporte pdf
@app.route('/reporte_pdf')
@login_required
def reporte_pdf():

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT nombre, categoria, autor, editorial, cantidad FROM libros WHERE estado=1")
    datos = cursor.fetchall()

    cursor.close()
    conexion.close()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    titulo = Paragraph("Inventario Biblioteca UEA", styles['Title'])
    espacio = Spacer(1, 20)

    data = [["Nombre", "Categoría", "Autor", "Editorial", "Cantidad"]]
    for fila in datos:
        data.append(list(fila))

    tabla = Table(data)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('GRID',(0,0),(-1,-1),1,colors.black)
    ]))

    doc.build([titulo, espacio, tabla])

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="reporte_libros.pdf",
        mimetype='application/pdf'
    )


###############

# run
if __name__ == '__main__':
    app.run(debug=True)