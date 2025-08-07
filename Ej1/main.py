from Ej1.conn import get_postgres_conn

def inicio():
    conn = get_postgres_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tablename 
        FROM pg_catalog.pg_tables
        WHERE schemaname NOT IN ('pg_catalog','information_schema')
    """)
    tables = cursor.fetchall()
    cursor.close()
    conn.close()
    print("-------------------------TABLES------------------")
    for table in tables:
        print(f"--{table[0]}---")
    if not tables:
        print("NO HAY TABLAS")
        return 'CargaInicial'
    else:
        print("TABLAS PRECARGADAS")
        return 'CargaIncremental'
