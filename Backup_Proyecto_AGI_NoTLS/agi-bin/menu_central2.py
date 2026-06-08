#!/usr/bin/env python3
import sys
import datetime
from db_conexion import obtener_conexion

# 1. Consumir encabezado AGI
while True:
    line = sys.stdin.readline().strip()
    if not line:
        break

def send_agi(comando):
    print(comando)
    sys.stdout.flush()
    return sys.stdin.readline().strip()

def reproducir(audio):
    # Forzamos la ruta completa para que Asterisk no se pierda
    send_agi(f'STREAM FILE {audio} ""')

def capturar_datos(audio, max_digitos):
    # GET DATA reproduce un audio y espera que el usuario teclee. Timeout: 8 seg.
    respuesta = send_agi(f'GET DATA {audio} 8000 {max_digitos}')
    # Asterisk responde algo como: 200 result=12345
    if "result=" in respuesta:
        partes = respuesta.split("result=")
        if len(partes) > 1:
            digitos = partes[1].split(' ')[0].strip()
            if digitos != '-1' and digitos != '':
                return digitos
    return None

def agregar_spam(numero):
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor()
        try:
            cursor.execute("INSERT INTO numeros_spam (numero) VALUES (%s)", (numero,))
            conexion.commit()
            reproducir("add_exito")
        except:
            # Falla si el número ya existe (Unique Key constraint)
            reproducir("add_existe")
        finally:
            cursor.close()
            conexion.close()

def eliminar_spam(numero):
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT id FROM numeros_spam WHERE numero = %s", (numero,))
        if cursor.fetchone():
            cursor.execute("DELETE FROM numeros_spam WHERE numero = %s", (numero,))
            conexion.commit()
            reproducir("del_exito")
        else:
            reproducir("del_error")
        cursor.close()
        conexion.close()

def informe_spam(numero):
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor()
        # Verificar si es spam
        cursor.execute("SELECT id FROM numeros_spam WHERE numero = %s", (numero,))
        es_spam = cursor.fetchone()
        
        if not es_spam:
            reproducir("info_no_spam")
        else:
            # Si es spam, verificar cuántas veces llamó hoy
            fecha_hoy = datetime.date.today()
            cursor.execute("SELECT cantidad FROM conteo_spam WHERE numero = %s AND fecha = %s", (numero, fecha_hoy))
            registro = cursor.fetchone()
            
            if registro and registro[0] > 0:
                cantidad = registro[0]
                reproducir("info_spam_parte1")
                # El motor nativo de Asterisk pronuncia el número en español
                send_agi(f'SAY NUMBER {cantidad} ""')
                reproducir("info_spam_parte2")
            else:
                reproducir("info_cero_llamadas")
        
        cursor.close()
        conexion.close()

def iniciar_menu():
    # Menú Principal: Espera 1 dígito (1, 2 o 3)
    opcion = capturar_datos("menu_admin", 1)
    
    if opcion == "1":
        numero = capturar_datos("ingrese_numero", 20)
        if numero: agregar_spam(numero)
    elif opcion == "2":
        numero = capturar_datos("ingrese_numero", 20)
        if numero: eliminar_spam(numero)
    elif opcion == "3":
        numero = capturar_datos("ingrese_numero", 20)
        if numero: informe_spam(numero)
    else:
        reproducir("opcion_invalida")

try:
    iniciar_menu()
except Exception as e:
    pass