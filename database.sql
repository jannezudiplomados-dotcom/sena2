-- ============================================
-- SISTEMA DE GESTION DE FICHAS SENA
-- Script SQL - Base de Datos (version corregida)
-- ============================================

CREATE DATABASE IF NOT EXISTS gestion_fichas3
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE gestion_fichas3;

-- ==============================
-- PROGRAMAS DE FORMACION
-- ==============================
CREATE TABLE IF NOT EXISTS programas_formacion (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre_programa VARCHAR(150) NOT NULL,
  descripcion TEXT,
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_nombre_programa (nombre_programa)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ==============================
-- FICHAS (GRUPOS)
-- ==============================
CREATE TABLE IF NOT EXISTS fichas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  numero_ficha VARCHAR(50) UNIQUE NOT NULL,
  programa_id INT,
  fecha_inicio DATE,
  fecha_fin DATE,
  estado VARCHAR(50) DEFAULT 'Activa',
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (programa_id) REFERENCES programas_formacion(id)
    ON DELETE SET NULL ON UPDATE CASCADE,
  INDEX idx_numero_ficha (numero_ficha),
  INDEX idx_programa_id (programa_id),
  INDEX idx_estado (estado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ==============================
-- USUARIOS (APRENDICES)
-- ==============================
CREATE TABLE IF NOT EXISTS usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  tipo_documento VARCHAR(20) NOT NULL DEFAULT 'CC',
  identificacion VARCHAR(50) NOT NULL,
  nombre VARCHAR(100) NOT NULL,
  apellidos VARCHAR(100) NOT NULL,
  telefono VARCHAR(20),
  correo_institucional VARCHAR(150),
  correo_personal VARCHAR(150),
  direccion_residencia VARCHAR(255),
  ficha_id INT,
  programa_id INT,
  firma_imagen VARCHAR(255),
  fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (ficha_id) REFERENCES fichas(id)
    ON DELETE SET NULL ON UPDATE CASCADE,
  FOREIGN KEY (programa_id) REFERENCES programas_formacion(id)
    ON DELETE SET NULL ON UPDATE CASCADE,
  UNIQUE KEY uq_identificacion (identificacion),
  INDEX idx_ficha_id (ficha_id),
  INDEX idx_programa_id (programa_id),
  INDEX idx_nombre_apellidos (nombre, apellidos)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ==============================
-- ADMIN (con roles y estado activo)
-- ==============================
CREATE TABLE IF NOT EXISTS admin (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,          -- hash Werkzeug (pbkdf2/scrypt), NO texto plano ni SHA simple
  nombre_completo VARCHAR(150),
  rol ENUM('superadmin','admin') NOT NULL DEFAULT 'admin',
  activo TINYINT(1) NOT NULL DEFAULT 1,
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_rol (rol),
  INDEX idx_activo (activo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ==============================
-- PLANTILLAS
-- ==============================
CREATE TABLE IF NOT EXISTS plantillas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(150) NOT NULL,
  archivo VARCHAR(255) NOT NULL,
  descripcion TEXT,
  fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ==============================
-- INTENTOS DE LOGIN (bloqueo temporal)
-- ==============================
CREATE TABLE IF NOT EXISTS intentos_login (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50),
  ip VARCHAR(64),
  exito TINYINT(1) NOT NULL DEFAULT 0,
  fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_username (username),
  INDEX idx_ip (ip),
  INDEX idx_fecha (fecha)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ==============================
-- LOG DE ACTIVIDADES (auditoria)
-- ==============================
CREATE TABLE IF NOT EXISTS log_actividades (
  id INT AUTO_INCREMENT PRIMARY KEY,
  admin_username VARCHAR(50),
  accion VARCHAR(30) NOT NULL,       -- crear / editar / eliminar / login / logout / generar
  entidad VARCHAR(30),               -- usuario / ficha / programa / plantilla / admin
  entidad_id INT,
  detalle VARCHAR(255),
  ip VARCHAR(64),
  fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_admin (admin_username),
  INDEX idx_accion (accion),
  INDEX idx_fecha (fecha)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ==============================
-- DATOS DE EJEMPLO (sin credenciales)
-- IMPORTANTE: el admin inicial se crea con: python crear_admin.py
-- (usa hash seguro y evita dejar admin/admin123 en el repositorio)
-- ==============================
INSERT INTO programas_formacion (nombre_programa, descripcion) VALUES
  ('Analisis y Desarrollo de Software', 'Programa tecnologico de desarrollo de aplicaciones'),
  ('Gestion Administrativa', 'Programa tecnico de gestion administrativa empresarial'),
  ('Contabilidad y Finanzas', 'Programa tecnologico de contabilidad y finanzas')
ON DUPLICATE KEY UPDATE nombre_programa = nombre_programa;
