#!/usr/bin/env python3
import sys
import datetime
import os
from db_conexion import obtener_conexion

# 1. Capturar la extensión que llega como argumento desde Asterisk
mi_extension = sys.argv[1] if len(sys.argv) > 1 else "desconocido"

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
    # Forzamos la ruta absoluta sin extensión. 
    # Si tu archivo se llama 'menu_admin.wav', Asterisk lo encontrará aquí.
    ruta_absoluta = f'/var/lib/asterisk/sounds/es/{audio}'
    send_agi(f'STREAM FILE {ruta_absoluta} ""')

def capturar_datos(audio, max_digitos):
    # CORRECCIÓN: También usamos ruta absoluta aquí, si no, Asterisk no encontrará el archivo
    ruta_absoluta = f'/var/lib/asterisk/sounds/es/{audio}'
    respuesta = send_agi(f'GET DATA {ruta_absoluta} 8000 {max_digitos}')
    
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
            # AHORA INCLUIMOS extension_propietario
            cursor.execute("INSERT INTO numeros_spam (numero, extension_propietario) VALUES (%s, %s)", (numero, mi_extension))
            conexion.commit()
            reproducir("add_exito")
        except Exception as e:
            send_agi(f'VERBOSE "ERROR AGREGAR: {str(e)}"')
            reproducir("add_existe")
        finally:
            cursor.close()
            conexion.close()

def eliminar_spam(numero):
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor()
        try:
            # Buscamos y borramos usando también la extensión para que cada quien gestione su lista
            cursor.execute("DELETE FROM numeros_spam WHERE numero = %s AND extension_propietario = %s", (numero, mi_extension))
            conexion.commit()
            if cursor.rowcount > 0:
                reproducir("del_exito")
            else:
                reproducir("del_error")
        except Exception as e:
            send_agi(f'VERBOSE "ERROR ELIMINAR: {str(e)}"')
        finally:
            cursor.close()
            conexion.close()

def informe_spam(numero):
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor()
        try:
            cursor.execute("SELECT id FROM numeros_spam WHERE numero = %s AND extension_propietario = %s", (numero, mi_extension))
            if not cursor.fetchone():
                reproducir("info_no_spam")
            else:
                fecha_hoy = datetime.date.today()
                cursor.execute("SELECT cantidad FROM conteo_spam WHERE numero = %s AND fecha = %s AND extension_propietario = %s", (numero, fecha_hoy, mi_extension))
                registro = cursor.fetchone()
                if registro and registro[0] > 0:
                    reproducir("info_spam_parte1")
                    send_agi(f'SAY NUMBER {registro[0]} ""')
                    reproducir("info_spam_parte2")
                else:
                    reproducir("info_cero_llamadas")
        except Exception as e:
            send_agi(f'VERBOSE "ERROR INFORME: {str(e)}"')
        finally:
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

# Ejecución sin el try-pass para ver errores reales en consola
iniciar_menu()
