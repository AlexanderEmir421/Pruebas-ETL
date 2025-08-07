import pandas as pd
import os
import glob
from Ej1.conn import get_engine_postgres

def cargar_csv():
    engine = get_engine_postgres()
    print("\n----------------------------CARGANDO CSV--------------------\n")
    files = glob.glob("/opt/airflow/Ej1/Csv/*.csv")
    print(f"--------------Csv encontrados: {files}-------------------------\n")
    for f in files:
        try:
            df = pd.read_csv(f)
            df.columns = [col.lower() for col in df.columns]
            table_name = os.path.splitext(os.path.basename(f))[0].lower()
            df.to_sql(table_name, engine, if_exists='replace', index=False)
            print(f"Tabla Insertada: {table_name}")
            print(df)
        except Exception as e:
            print(f"ERROR: {e}")
    return 'cargarinicialsupabase'

