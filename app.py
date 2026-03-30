import os
from flask import Flask, render_template, request, redirect, url_for
from conexion.conexion import obtener_conexion
from werkzeug.utils import secure_filename

from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin


from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from flask import send_file
import io
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet



app = Flask(__name__)
app.secret_key = "clave_secreta"

# =========================
# LOGIN CONFIG
# =========================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# =========================
# IMÁGENES
# =========================
UPLOAD_FOLDER = 'static/img/libros'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# =========================
# MODELO USUARIO
# =========================
class Usuario(UserMixin):
    def __init__(self, id, nombre, email, password, tipo):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.password = password
        self.tipo = tipo

    def get_id(self):
        return f"{self.tipo}-{self.id}"


# =========================
# CARGAR USUARIO
# =========================
@login_manager.user_loader
def load_user(user_id):

    try:
        tipo, id_real = user_id.split("-")
    except:
        return None

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    if tipo == "usuario":
        cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (id_real,))
        user = cursor.fetchone()

        cursor.close()
        conexion.close()

        if user:
            return Usuario(user[0], user[1], user[2], user[3], "usuario")

    elif tipo == "admin":
        cursor.execute("SELECT * FROM administradores WHERE id_admin = %s", (id_real,))
        admin = cursor.fetchone()

        cursor.close()
        conexion.close()

        if admin:
            return Usuario(admin[0], admin[1], admin[2], admin[3], "admin")

    return None


# =========================
# RUTAS
# =========================

@app.route('/')
def inicio():
    return redirect(url_for('login'))


@app.route('/libros')
@login_required
def libros():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM libros")
    libros = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template('libros.html', libros=libros)


# SOLO ADMIN
@app.route('/agregar', methods=['GET','POST'])
@login_required
def agregar():

    if current_user.tipo != "admin":
        return "Acceso denegado", 403

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
        INSERT INTO libros(nombre,categoria,descripcion,autor,editorial,cantidad,imagen)
        VALUES(%s,%s,%s,%s,%s,%s,%s)
        """,(nombre,categoria,descripcion,autor,editorial,cantidad,nombre_imagen))

        conexion.commit()

        cursor.close()
        conexion.close()

        return redirect(url_for('libros'))

    return render_template('agregar.html')


# SOLO ADMIN
@app.route('/eliminar/<int:id>')
@login_required
def eliminar(id):

    if current_user.tipo != "admin":
        return "Acceso denegado", 403

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("DELETE FROM libros WHERE id_libro=%s",(id,))
    conexion.commit()

    cursor.close()
    conexion.close()

    return redirect(url_for('libros'))


# =========================
# REGISTRO
# =========================
@app.route('/registro', methods=['GET','POST'])
def registro():

    if request.method == 'POST':

        nombre = request.form['nombre']
        email = request.form['email']
        telefono = request.form['telefono']
        password = request.form['password']

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            "INSERT INTO usuarios(nombre,email,telefono,password) VALUES(%s,%s,%s,%s)",
            (nombre,email,telefono,password)
        )

        conexion.commit()

        cursor.close()
        conexion.close()

        return redirect(url_for('login'))

    return render_template('registro.html')




# =========================
# 
# =========================

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):

    if current_user.tipo != "admin":
        return "Acceso denegado", 403

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    # Obtener libro
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

# =========================
# LOGIN
# =========================
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # usuarios
        cursor.execute("SELECT * FROM usuarios WHERE email=%s AND password=%s",(email, password))
        user = cursor.fetchone()
        tipo = "usuario"

        # admin
        if not user:
            cursor.execute("SELECT * FROM administradores WHERE email=%s AND password=%s",(email, password))
            user = cursor.fetchone()
            tipo = "admin"

        cursor.close()
        conexion.close()

        if user:
            usuario = Usuario(user[0], user[1], user[2], user[3], tipo)
            login_user(usuario)

            next_page = request.args.get('next')
            return redirect(next_page or url_for('libros'))

        else:
            return render_template('login.html', error="Credenciales incorrectas")

    return render_template('login.html')


# =========================
# LOGOUT
# =========================
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# =========================
# RESET SESIÓN (IMPORTANTE)
# =========================
@app.route('/reset')
def reset():
    logout_user()
    return "Sesión reiniciada"

# =========================
# REPORTE PDF
# =========================

@app.route('/reporte_pdf')
@login_required
def reporte_pdf():

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT nombre, categoria, autor, editorial, cantidad FROM libros")
    datos = cursor.fetchall()

    cursor.close()
    conexion.close()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    # 🔥 TÍTULO
    titulo = Paragraph("📚 Inventario Biblioteca UEA", styles['Title'])

    # Espacio
    espacio = Spacer(1, 20)

    # Tabla
    data = [["Nombre", "Categoría", "Autor", "Editorial", "Cantidad"]]

    for fila in datos:
        data.append(list(fila))

    tabla = Table(data)

    estilo = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('GRID',(0,0),(-1,-1),1,colors.black)
    ])

    tabla.setStyle(estilo)

    elementos = []
    elementos.append(titulo)
    elementos.append(espacio)
    elementos.append(tabla)

    doc.build(elementos)

    buffer.seek(0)

    return send_file(buffer, as_attachment=True,
                     download_name="reporte_libros.pdf",
                     mimetype='application/pdf')


# =========================
# RUN
# =========================
if __name__ == '__main__':
    app.run(debug=True)