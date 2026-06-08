#!/usr/bin/env python3
import sys
import datetime
from db_conexion import obtener_conexion

# Capturar el número que llama (arg 1) y el número destino (arg 2 si lo necesitas)
numero_llamante = sys.argv[1] if len(sys.argv) > 1 else "Desconocido"

def send_agi(comando):
    print(comando)
    sys.stdout.flush()
    return sys.stdin.readline().strip()

try:
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor()
        
        # 1. Verificar si es SPAM
        cursor.execute("SELECT id FROM numeros_spam WHERE numero = %s", (numero_llamante,))
        resultado = cursor.fetchone()
        
        if resultado:
            send_agi('SET VARIABLE ES_SPAM "SI"')
            
            # 2. Registrar el intento en conteo_spam (Incluyendo extension_propietario)
            # Nota: Usamos la extensión del llamante como propietario
            fecha_hoy = datetime.date.today()
            sql_conteo = """
                INSERT INTO conteo_spam (numero, extension_propietario, fecha, cantidad) 
                VALUES (%s, %s, %s, 1) 
                ON DUPLICATE KEY UPDATE cantidad = cantidad + 1
            """
            cursor.execute(sql_conteo, (numero_llamante, numero_llamante, fecha_hoy))
            conexion.commit()
        else:
            send_agi('SET VARIABLE ES_SPAM "NO"')
            
        cursor.close()
        conexion.close()
    else:
        send_agi('SET VARIABLE ES_SPAM "NO"')
except Exception as e:
    send_agi(f'VERBOSE "ERROR VALIDACION: {str(e)}"')
    send_agi('SET VARIABLE ES_SPAM "NO"')
