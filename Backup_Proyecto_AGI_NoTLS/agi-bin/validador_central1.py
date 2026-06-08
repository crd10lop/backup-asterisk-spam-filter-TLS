#!/usr/bin/env python3
import sys
import datetime
from db_conexion import obtener_conexion

# 1. Consumir el encabezado que envía Asterisk (OBLIGATORIO EN AGI)
while True:
    line = sys.stdin.readline().strip()
    if not line:
        break

def send_agi(comando):
    # Enviar comando a Asterisk y obligar a que salga de la memoria caché
    print(comando)
    sys.stdout.flush()
    return sys.stdin.readline().strip()

try:
    # 2. Capturar el número que llama (Asterisk lo pasa como argumento 1)
    if len(sys.argv) > 1:
        numero_llamante = sys.argv[1]
    else:
        numero_llamante = "Desconocido"

    conexion = obtener_conexion()
    if conexion and conexion.is_connected():
        cursor = conexion.cursor()
        
        # 3. Verificar si el número está en la lista negra
        cursor.execute("SELECT id FROM numeros_spam WHERE numero = %s", (numero_llamante,))
        resultado = cursor.fetchone()
        
        if resultado:
            # ES SPAM: Le decimos a Asterisk que cambie la variable a "SI"
            send_agi('SET VARIABLE ES_SPAM "SI"')
            
            # Sumar +1 al contador de hoy (Insertar o actualizar si ya existe)
            fecha_hoy = datetime.date.today()
            sql_conteo = """
                INSERT INTO conteo_spam (numero, fecha, cantidad) 
                VALUES (%s, %s, 1) 
                ON DUPLICATE KEY UPDATE cantidad = cantidad + 1
            """
            cursor.execute(sql_conteo, (numero_llamante, fecha_hoy))
            conexion.commit()
        else:
            # NO ES SPAM: Dejamos pasar la llamada
            send_agi('SET VARIABLE ES_SPAM "NO"')
            
        cursor.close()
        conexion.close()
    else:
        # Si la base de datos falla, por seguridad dejamos pasar la llamada
        send_agi('SET VARIABLE ES_SPAM "NO"')

except Exception as e:
    # Captura de errores para que Asterisk no colapse
    send_agi('SET VARIABLE ES_SPAM "NO"')