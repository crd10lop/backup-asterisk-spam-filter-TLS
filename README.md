# Backup y Migración de PBX Asterisk (Filtro Spam AGI y TLS)

**Autor:** Cristian David Diez Lopez

Este repositorio contiene la copia de seguridad completa de la central telefónica Asterisk con soporte de llamadas seguras (TLS/SRTP) y un menú interactivo AGI desarrollado en Python para la gestión y bloqueo de llamadas SPAM.

## 1. Requisitos Previos en el Nuevo Servidor

Antes de restaurar los archivos, el nuevo servidor debe tener instalado:

* Asterisk (con soporte PJSIP).
* MySQL Server (MariaDB/MySQL).
* Python 3 y `pip`.
* Librerías: `sudo apt install sox` y `pip3 install mysql-connector-python`.

## 2. Proceso de Restauración

### A. Restaurar Archivos de Asterisk

Descomprime el archivo `backup_asterisk_spam.tar.gz` en el nuevo servidor e ingresa a la carpeta `tmp_asterisk`. Luego ejecuta:

```bash
# 1. Restaurar configuraciones (Reemplazar la IP pública en pjsip.conf si el servidor es nuevo)
sudo cp -r etc/asterisk/* /etc/asterisk/

# 2. Restaurar scripts AGI
sudo cp -r var/lib/asterisk/agi-bin/* /var/lib/asterisk/agi-bin/

# 3. Restaurar audios
sudo mkdir -p /var/lib/asterisk/sounds/es
sudo cp -r var/lib/asterisk/sounds/es/* /var/lib/asterisk/sounds/es/
```

### B. Restaurar Base de Datos

```bash
# Entrar a MySQL como root para crear base de datos y usuario
mysql -u root -p
> CREATE DATABASE db_agi_spam;
> CREATE USER 'usr_agi'@'localhost' IDENTIFIED BY 'Asterisk_2026!';
> GRANT ALL PRIVILEGES ON db_agi_spam.* TO 'usr_agi'@'localhost';
> FLUSH PRIVILEGES;
> EXIT;

# Importar el respaldo
mysql -u usr_agi -p'Asterisk_2026!' db_agi_spam < db_backup/db_agi_spam.sql
```

### C. Ajuste de Permisos y Reinicio

```bash
# Otorgar propiedad a Asterisk
sudo chown -R asterisk:asterisk /etc/asterisk/
sudo chown -R asterisk:asterisk /var/lib/asterisk/agi-bin/
sudo chown -R asterisk:asterisk /var/lib/asterisk/sounds/es/

# Permisos de ejecución a Python
sudo chmod +x /var/lib/asterisk/agi-bin/*.py

# Reiniciar servicio
sudo systemctl restart asterisk
```

## 3. Comandos de Verificación (Troubleshooting)

Para confirmar que el sistema migrado funciona correctamente, ingresa a la consola de Asterisk (`sudo asterisk -rvvv`) y utiliza los siguientes comandos:

* **Verificar Transporte TLS:** `pjsip show transports` (Debe mostrar el transporte TLS en estado "Ready" o "Active").
* **Verificar Extensiones Registradas:** `pjsip show endpoints` (Las extensiones 100, 110, etc., deben decir "Reachable").
* **Verificar Caché de Audios (Opcional):** `file show sounds`
* **Recargar Plan de Llamadas:** `dialplan reload`

### Diagnóstico de TLS y Captura de Errores

Si las extensiones no registran o las llamadas seguras fallan, usa estas herramientas para ver qué está pasando a nivel de red y de transporte antes de tocar la configuración:

```bash
# Ver el tráfico en el puerto seguro en tiempo real (útil para detectar handshakes TLS fallidos)
sudo tcpdump -i any port 5061 -vv

# Confirmar que Asterisk está realmente escuchando en el puerto 5061
sudo ss -tulpn | grep 5061

# Inspeccionar el estado del transporte TLS sin entrar a la consola
sudo asterisk -rx "pjsip show transport transport-tls"
```

Para depurar el menú AGI de bloqueo de SPAM, entra a la consola y activa el modo debug:

```bash
sudo asterisk -rvvv
agi set debug on
```

### Reinicio Completo y Limpieza de Caché

Usa este procedimiento cuando los cambios en los archivos `.conf` no se reflejan o Asterisk arranca con configuraciones viejas. Fuerza una relectura completa eliminando la base de datos interna y la caché:

```bash
# 1. Detener completamente
sudo systemctl stop asterisk
sudo killall -9 asterisk

# 2. Eliminar el archivo de caché de configuración (esto obliga a Asterisk a releer los archivos .conf)
sudo rm -rf /var/lib/asterisk/astdb*
sudo rm -rf /var/cache/asterisk/*

# 3. Arrancar de nuevo
sudo systemctl start asterisk
sudo asterisk -rvvv
```

## 4. Configuración General en Clientes SIP (Zoiper/MicroSIP)

Para conectar cualquier aplicativo móvil o de escritorio a esta central, los parámetros estándar son:

* **Domain / Host:** `IP_PUBLICA_DEL_SERVIDOR:5061` (Es crucial usar el puerto 5061 para TLS).
* **Username / Extension:** `110` (o el número asignado).
* **Password:** `La_contraseña_secreta_configurada_en_pjsip`.
* **Network / Transport:** Seleccionar obligatoriamente TLS.
* **Encryption / SRTP:** Configurar como Obligatorio (Mandatory) o Activo. Si no se activa, la llamada se caerá a los 30 segundos.
