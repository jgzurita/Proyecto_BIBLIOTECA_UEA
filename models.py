import sqlite3


class Producto:
    def __init__(self, id, nombre, cantidad, precio):
        self.id = id
        self.nombre = nombre
        self.cantidad = cantidad
        self.precio = precio

    def datos(self):
        return (self.nombre, self.cantidad, self.precio)





class Inventario:
    def __init__(self):
        self.productos = {}  # Diccionario {id: Producto}

    def conectar(self):
        return sqlite3.connect("inventario.db")

    def agregar(self, producto):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO productos (nombre, cantidad, precio) VALUES (?, ?, ?)",
            producto.datos()
        )
        conn.commit()
        conn.close()

    def obtener_todos(self):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos")
        datos = cursor.fetchall()
        conn.close()
        return datos

    def eliminar(self, id):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM productos WHERE id=?", (id,))
        conn.commit()
        conn.close()