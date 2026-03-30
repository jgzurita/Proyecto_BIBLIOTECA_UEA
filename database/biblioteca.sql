CREATE DATABASE IF NOT EXISTS biblioteca;
USE biblioteca;

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;

-- =========================
-- TABLA ADMINISTRADORES
-- =========================
CREATE TABLE administradores (
  id_admin INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  email VARCHAR(100) UNIQUE,
  password VARCHAR(100)
);

INSERT INTO administradores (nombre, email, password)
VALUES ('Juan Zurita', 'admin@biblioteca.com', '1234');

-- =========================
-- TABLA USUARIOS (LOGIN)
-- =========================
CREATE TABLE usuarios (
  id_usuario INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  email VARCHAR(100) UNIQUE,
  telefono VARCHAR(20),
  password VARCHAR(100) NOT NULL
);

-- usuario de prueba para login
INSERT INTO usuarios (nombre, email, telefono, password)
VALUES ('Carlos Perez', 'carlos@gmail.com', '099999999', '1234');

-- =========================
-- TABLA LIBROS
-- =========================
CREATE TABLE libros (
  id_libro INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(150) NOT NULL,
  categoria VARCHAR(100),
  descripcion TEXT,
  autor VARCHAR(100),
  editorial VARCHAR(100),
  anio_publicacion INT,
  cantidad INT DEFAULT 1,
  imagen VARCHAR(255)
);

INSERT INTO libros (nombre, categoria, descripcion, autor, editorial, anio_publicacion, cantidad, imagen)
VALUES ('Cien años de soledad', 'Novela', 'Libro clásico latinoamericano', 'Gabriel Garcia Marquez', 'Sudamericana', 1967, 5, NULL);

-- =========================
-- TABLA PRESTAMOS
-- =========================
CREATE TABLE prestamos (
  id_prestamo INT AUTO_INCREMENT PRIMARY KEY,
  id_libro INT,
  id_usuario INT,
  id_admin INT,
  fecha_prestamo DATE,
  fecha_devolucion DATE,
  estado VARCHAR(50),

  FOREIGN KEY (id_libro) REFERENCES libros(id_libro),
  FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
  FOREIGN KEY (id_admin) REFERENCES administradores(id_admin)
);

INSERT INTO prestamos (id_libro, id_usuario, id_admin, fecha_prestamo, fecha_devolucion, estado)
VALUES (1, 1, 1, '2026-06-01', '2026-06-15', 'Prestado');

COMMIT;