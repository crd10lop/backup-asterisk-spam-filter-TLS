import mysql.connector
from mysql.connector import Error

def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            database='db_agi_spam',
            user='usr_agi',
            password='Asterisk_2026!'
        )
        return conexion
    except Error as e:
        # Si hay error (ej. base de datos caída), devuelve None
        return None