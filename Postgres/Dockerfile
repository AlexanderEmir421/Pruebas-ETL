FROM postgres:13

# Copiar bash init para crear la db de origen
COPY 01-initdb.sh /docker-entrypoint-initdb.d/

# Establecer permisos adecuados
RUN chown postgres:postgres /docker-entrypoint-initdb.d/* && \
    chmod 755 /docker-entrypoint-initdb.d/01-initdb.sh