-- 1. Eliminar la base de datos anterior de forma segura
DROP DATABASE IF EXISTS db_agi_spam;

-- 2. Crear la nueva base de datos
CREATE DATABASE db_agi_spam CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE db_agi_spam;

-- 3. Crear tabla de números bloqueados (Con campo de dueño)
CREATE TABLE numeros_spam (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero VARCHAR(20) NOT NULL,
    extension_propietario VARCHAR(20) NOT NULL,
    fecha_bloqueo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY numero_por_usuario (numero, extension_propietario)
);

-- 4. Crear tabla de métricas y conteo
CREATE TABLE conteo_spam (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero VARCHAR(20) NOT NULL,
    extension_propietario VARCHAR(20) NOT NULL,
    fecha DATE NOT NULL,
    cantidad INT DEFAULT 1,
    UNIQUE KEY conteo_diario (numero, extension_propietario, fecha)
);

-- 5. Garantizar permisos al usuario de Asterisk
CREATE USER IF NOT EXISTS "usr_agi"@"localhost" IDENTIFIED BY "Asterisk_2026!";
GRANT ALL PRIVILEGES ON db_agi_spam.* TO "usr_agi"@"localhost";
FLUSH PRIVILEGES;
