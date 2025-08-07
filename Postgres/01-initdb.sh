#!/bin/bash
set -e

echo "[INIT] Iniciando script de inicialización" >&2

## --------------------------------------------
## 1. CONFIGURACIÓN 
## --------------------------------------------

# Creando acceso Usuario y contraseña 
APP_USER="${POSTGRES_USUARIO}"
APP_PASSWORD="${POSTGRES_PASSWORD_USUARIO}"

# Base de datos para copiar las tablas
APP_DB="${POSTGRES_DB_REPLICA}"

## --------------------------------------------
## 2. FUNCIONES AUXILIARES
## --------------------------------------------

run_psql() {
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres <<< "$1"
}

run_psql_continue() {
    psql --username "$POSTGRES_USER" --dbname postgres <<< "$1" || echo "[INFO] Operación omitida: $1" >&2
}

## --------------------------------------------
## 3. CREACIÓN DE USUARIO
## --------------------------------------------

echo "[INIT] Creando usuario $APP_USER" >&2
run_psql_continue "CREATE USER \"$APP_USER\" WITH PASSWORD '$APP_PASSWORD' CREATEDB;"

## --------------------------------------------
## 4. CREACIÓN DE BASE DE DATOS
## --------------------------------------------

echo "[INIT] Creando base de datos $APP_DB con propietario $APP_USER" >&2
run_psql_continue "CREATE DATABASE \"$APP_DB\" WITH OWNER \"$APP_USER\";"

## --------------------------------------------
## 5. ASIGNACIÓN DE PERMISOS EN LA BASE
## --------------------------------------------

echo "[INIT] Asignando permisos completos a $APP_USER sobre $APP_DB" >&2

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$APP_DB" <<-EOSQL
    GRANT CONNECT ON DATABASE "$APP_DB" TO "$APP_USER";
    GRANT USAGE ON SCHEMA public TO "$APP_USER";
    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO "$APP_USER";
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO "$APP_USER";
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO "$APP_USER";
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO "$APP_USER";
    ALTER SCHEMA public OWNER TO "$APP_USER";
EOSQL

## --------------------------------------------
## FINALIZACIÓN
## --------------------------------------------

echo "[INIT] Script de inicialización completado exitosamente" >&2