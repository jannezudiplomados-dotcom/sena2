"""Crea o reinicia un administrador con contrasena hasheada de forma segura.

Uso interactivo:
    python crear_admin.py

Uso por argumentos:
    python crear_admin.py --username admin --nombre "Administrador" --rol superadmin

Este script reemplaza el antiguo admin/admin123 quemado en database.sql.
"""
import argparse
import getpass
import sys

from werkzeug.security import generate_password_hash
from models import Database


def upsert_admin(username, password, nombre, rol):
    password_hash = generate_password_hash(password)
    existente = Database.execute_query(
        "SELECT id FROM admin WHERE username = %s", (username,), fetch_one=True
    )
    if existente:
        Database.execute_query(
            "UPDATE admin SET password = %s, nombre_completo = %s, rol = %s, activo = 1 WHERE username = %s",
            (password_hash, nombre, rol, username), commit=True
        )
        print(f"Administrador '{username}' actualizado.")
    else:
        Database.execute_query(
            "INSERT INTO admin (username, password, nombre_completo, rol, activo) VALUES (%s, %s, %s, %s, 1)",
            (username, password_hash, nombre, rol), commit=True
        )
        print(f"Administrador '{username}' creado.")


def main():
    parser = argparse.ArgumentParser(description='Crear/reiniciar administrador')
    parser.add_argument('--username')
    parser.add_argument('--nombre')
    parser.add_argument('--rol', choices=['superadmin', 'admin'], default='superadmin')
    args = parser.parse_args()

    username = args.username or input('Usuario: ').strip()
    nombre = args.nombre or input('Nombre completo: ').strip()
    rol = args.rol

    password = getpass.getpass('Contrasena: ')
    confirmar = getpass.getpass('Confirmar contrasena: ')
    if password != confirmar:
        print('Las contrasenas no coinciden.')
        sys.exit(1)
    if len(password) < 8:
        print('La contrasena debe tener al menos 8 caracteres.')
        sys.exit(1)

    upsert_admin(username, password, nombre or username, rol)


if __name__ == '__main__':
    main()
