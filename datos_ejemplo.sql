-- ============================================
-- DATOS DE EJEMPLO (IMAGINARIOS)
-- Sistema de Gestion de Fichas SENA
-- --------------------------------------------
-- TODOS los datos de este archivo son FICTICIOS / IMAGINARIOS.
-- No corresponden a personas reales. Uso exclusivo para pruebas.
-- Ejecutar DESPUES de database.sql:
--   mysql -u sena_app -p gestion_fichas < datos_ejemplo.sql
-- ============================================

USE gestion_fichas;

-- Fichas de ejemplo (asociadas a programas ya insertados en database.sql)
INSERT INTO fichas (numero_ficha, programa_id, fecha_inicio, fecha_fin, estado) VALUES
  ('2801122', (SELECT id FROM programas_formacion WHERE nombre_programa = 'Analisis y Desarrollo de Software' LIMIT 1), '2026-02-01', '2027-08-01', 'Activa'),
  ('2801123', (SELECT id FROM programas_formacion WHERE nombre_programa = 'Gestion Administrativa' LIMIT 1), '2026-03-01', '2027-03-01', 'Activa'),
  ('2801124', (SELECT id FROM programas_formacion WHERE nombre_programa = 'Contabilidad y Finanzas' LIMIT 1), '2025-08-01', '2026-11-01', 'Finalizada')
ON DUPLICATE KEY UPDATE numero_ficha = numero_ficha;

-- Aprendices de ejemplo (IMAGINARIOS) con firmas imaginarias en static/firmas/
INSERT INTO usuarios
  (tipo_documento, identificacion, nombre, apellidos, telefono, correo_institucional, correo_personal, direccion_residencia, ficha_id, programa_id, firma_imagen)
VALUES
  ('CC', '1000000001', 'Ana Maria', 'Gomez Lopez', '3000000001', 'ana.gomez@soy.sena.edu.co', 'ana.ejemplo@example.com', 'Calle Ficticia 1 #10-20', (SELECT id FROM fichas WHERE numero_ficha='2801122'), (SELECT id FROM programas_formacion WHERE nombre_programa='Analisis y Desarrollo de Software' LIMIT 1), 'firma_ana_gomez.png'),
  ('TI', '1000000002', 'Carlos Andres', 'Ruiz Perez', '3000000002', 'carlos.ruiz@soy.sena.edu.co', 'carlos.ejemplo@example.com', 'Carrera Imaginaria 2 #11-22', (SELECT id FROM fichas WHERE numero_ficha='2801122'), (SELECT id FROM programas_formacion WHERE nombre_programa='Analisis y Desarrollo de Software' LIMIT 1), 'firma_carlos_ruiz.png'),
  ('CC', '1000000003', 'Laura Valentina', 'Torres Diaz', '3000000003', 'laura.torres@soy.sena.edu.co', 'laura.ejemplo@example.com', 'Avenida Ejemplo 3 #12-33', (SELECT id FROM fichas WHERE numero_ficha='2801123'), (SELECT id FROM programas_formacion WHERE nombre_programa='Gestion Administrativa' LIMIT 1), 'firma_laura_torres.png'),
  ('CC', '1000000004', 'Juan David', 'Martinez Soto', '3000000004', 'juan.martinez@soy.sena.edu.co', 'juan.ejemplo@example.com', 'Diagonal Ficticia 4 #13-44', (SELECT id FROM fichas WHERE numero_ficha='2801123'), (SELECT id FROM programas_formacion WHERE nombre_programa='Gestion Administrativa' LIMIT 1), 'firma_juan_martinez.png'),
  ('CE', '1000000005', 'Sofia Alejandra', 'Diaz Ramirez', '3000000005', 'sofia.diaz@soy.sena.edu.co', 'sofia.ejemplo@example.com', 'Transversal Imaginaria 5 #14-55', (SELECT id FROM fichas WHERE numero_ficha='2801124'), (SELECT id FROM programas_formacion WHERE nombre_programa='Contabilidad y Finanzas' LIMIT 1), 'firma_sofia_diaz.png')
ON DUPLICATE KEY UPDATE identificacion = identificacion;
