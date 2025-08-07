from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from supabase import create_client
from sqlalchemy import create_engine
import datetime as dt
import os
import psycopg2
import pandas as pd
import glob



tablesG=[("dimdate", "dateid"),("dimcustomersegment", "segmentid"),("factsales", "salesid"),("dimproduct", "productid")]
tablesI=["dimdate","factsales","dimproduct"] #Tablas tecnica ultimo id (inserta apartir del ultimo id en mi tabla StgLog)
tablesE=["dimcustomersegment"]#Tablas tecnica estado (Hace un Full-refresh e identifica tablas borradas)



def load_supabase(table,df,batch=10):
    supabase = create_client(os.getenv('URL_SUPABASE'), os.getenv('TOKEN_SUPABASE'))
    data = df.to_dict(orient="records")
    for i in range(0,len(data),batch):
        try:
            supabase.table(table).insert(data[i:i+batch]).execute()
            print(f"---------------------------------------Datos insertados Correctamente {table}------------------------\n ")
        except Exception as e:
            print(f"Error insertando en {table}: {e}")
            

def set_stanging(table,id,df):
    supabase = create_client(os.getenv('URL_SUPABASE'), os.getenv('TOKEN_SUPABASE'))
    for index,row in df.iterrows(): 
        supabase.table(table).update({
            "state":row["state"]
        }).eq(id,row[id]).execute()


def update_inactive(table,id,engine):
    stanging="stg_" + table
    df= pd.read_sql(f'SELECT * FROM "{table}"',engine)
    supabase = create_client(os.getenv('URL_SUPABASE'), os.getenv('TOKEN_SUPABASE'))
    supabase= supabase.table(stanging).select("*").execute()
    df_supabase = pd.DataFrame(supabase.data)
    
    if not df_supabase.empty:
        comparison = df.merge(df_supabase,on=[id],how='outer',indicator=True,suffixes=('_PG', '_SP'))
        print(f"\n ---------------FULL OTHER JOIN-------------\n {comparison}\n")
        # Renombrar columnas que terminan en '_PG' les quitamos el sufijo
        rename_pg_cols = {col: col[:-3] for col in comparison.columns if col.endswith('_PG')}
        # Eliminar columnas que terminan en '_SP'
        drop_sp_cols = [col for col in comparison.columns if col.endswith('_SP')]
        
        new_customers = (
        comparison[comparison["_merge"] == 'left_only']
        .copy()
        .assign(state="active")
        .rename(columns=rename_pg_cols)
        .drop(['_merge'] + drop_sp_cols, axis=1)
        )
        
        print(f"\n ---------------Nuevos Datos-------------\n {new_customers}\n")
        #estos son elementos borrados de la tabla origen
        condicion = (
        (comparison["_merge"] == 'right_only') &
        (comparison["state"] != "inactive")
        )
        delete_customers = (
            comparison[condicion]
            .copy()
            .assign(state="inactive")
            .rename(columns={col: col[:-3] for col in comparison.columns if col.endswith('_SP')})
            .drop(['_merge'] + [col for col in comparison.columns if col.endswith('_PG')], axis=1)
        )
        print(f"\n ---------------Datos borrados-------------\n {delete_customers}\n")
        load_supabase(stanging,new_customers)
        load_supabase(table,new_customers)
        set_stanging(stanging,id,delete_customers)
        
        if not new_customers.empty:    
            last_id=new_customers[id].max()
            set_lastid_logs(table,last_id)
    else:
        print("\n -----------------No hay datos iniciales------------------------")
    
def update_lastid(table,id,engine):
    supabase = create_client(os.getenv('URL_SUPABASE'), os.getenv('TOKEN_SUPABASE'))
    result = supabase.table("StgLogs").select("last_id").eq("table_name", table).execute()
    last_id = result.data[0].get('last_id')
    if table == "factsales":#SE PUEDE MEJORAR
        df = pd.read_sql(f'SELECT * FROM "{table}" WHERE "{id}" > \'{last_id}\'', engine)
    else:
        last_id = int(last_id)
        df = pd.read_sql(f'SELECT * FROM "{table}" WHERE "{id}" > {last_id}', engine)
    if not df.empty:
        last_id_supabase = df[id].max()
        print(f"\n ---------------SE ENCONTRAROS DATOS NUEVOS | ULTIMO ID DE LA TABLA:{last_id}-----------------\n")
        load_supabase(table, df)
        set_lastid_logs(table,last_id_supabase)
    else:
        print("\n ---------------NO HAY DATOS NUEVOS PARA INSERTAR EN SUPABASE-----------------\n")

    
def set_lastid_logs(name_table,last_id):
    fecha_actual_utc = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S+00')
    supabase = create_client(os.getenv('URL_SUPABASE'), os.getenv('TOKEN_SUPABASE'))
    supabase.table("StgLogs").update({
        "last_id":str(last_id),
        "last_load":fecha_actual_utc
    }).eq("table_name",name_table).execute()


def set_inactive(table,id,engine):
    stanging="stg_" + table
    df= pd.read_sql(f'SELECT * FROM "{table}"',engine)
    print(f"\n --------------\n {df} \n --------------\n")
    df_state = df.assign(state='active')
    load_supabase(stanging,df_state)
    load_supabase(table,df) 
    last_id_supabase = df[id].max()
    set_lastid_logs(table, last_id_supabase)


def set_lastid(table, cond,engine):
    df = pd.read_sql(f'SELECT * FROM "{table}"', engine)
    print(df)
    if not df.empty:
        last_id_supabase= df[cond].max()
        print(f"\n ---------------SE ENCONTRAROS DATOS PARA LA CARGA INICIAL | ULTIMO ID DE LA TABLA:{last_id_supabase}-----------------\n")
        
        load_supabase(table, df)
        set_lastid_logs(table, last_id_supabase)
    else:
        print("\n ---------------NO HAY DATOS PARA INSERTAR EN SUPABASE CASO INICIAL-----------------\n")



def cargaincremental_function(table, id):
    def call():
        engine = create_engine(
        f"postgresql+psycopg2://{os.getenv('POSTGRES_USUARIO')}:{os.getenv('POSTGRES_PASSWORD_USUARIO')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB_REPLICA')}"
        )
        if table in tablesI:
            update_lastid(table,id,engine)
        elif table in tablesE:
            update_inactive(table,id,engine)
    return call

def cargainicial_function(table, id):
    def call():
        engine = create_engine(
        f"postgresql+psycopg2://{os.getenv('POSTGRES_USUARIO')}:{os.getenv('POSTGRES_PASSWORD_USUARIO')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB_REPLICA')}"
        )
        if table in tablesI:
            set_lastid(table,id,engine)
        elif table in tablesE:
            set_inactive(table,id,engine)
    return call

def cargar_csv():
    engine = create_engine(
        f"postgresql+psycopg2://{os.getenv('POSTGRES_USUARIO')}:{os.getenv('POSTGRES_PASSWORD_USUARIO')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB_REPLICA')}"
    )
    print("\n----------------------------CARGANDO CSV--------------------\n")
    files = glob.glob("/opt/airflow/data/*.csv")
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
        

def inicio():
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        dbname=os.getenv("POSTGRES_DB_REPLICA"),
        user=os.getenv("POSTGRES_USUARIO"),
        password=os.getenv("POSTGRES_PASSWORD_USUARIO"),
        port=os.getenv("POSTGRES_PORT")
    )
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








#---------------------------------------------AIRFLOW------------------------------------------
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': dt.datetime(2025, 7, 19),
    'retries': 1,
    'retry_delay': dt.timedelta(minutes=5),
}

with DAG(
    'Ejercicio1',
    default_args=default_args,
    description='Flujo condicional: crear tablas si no existen o Actualizarlas',
    schedule_interval='0 0 * * *', #Se ejecuta diariamente a las 00:00
    catchup=False,
) as dag:
    
    task1 = BranchPythonOperator(
        task_id='Inicio',
        python_callable=inicio
    )

    task2 = BashOperator(
        task_id='CargaIncremental',
        bash_command='echo "CARGA INCREMENTAL"'
    )

    task3 = PythonOperator(
        task_id='CargaInicial',
        python_callable=cargar_csv
    )
    
    finInit = EmptyOperator(task_id='finCargaInicial')
    finIncremental = EmptyOperator(task_id='finCargaIncremental')
    
    task_cargasiniciales_sp=[]
    task_cargasincrementales_sp=[]
    for table, id in tablesG:
        task_inicial=PythonOperator(
            task_id=f"CreaTabla{table}",
            python_callable=cargainicial_function(table, id)
        )
        task_cargasiniciales_sp.append(task_inicial)
    
    for table, id in tablesG:
        task_inicial=PythonOperator(
            task_id=f"Update{table}",
            python_callable=cargaincremental_function(table, id)
        )
        task_cargasincrementales_sp.append(task_inicial)
    
    task1 >> task2 >> task_cargasincrementales_sp #Carga Incremental
    task1 >> task3 >> task_cargasiniciales_sp #Primer carga en Supabase
    task_cargasiniciales_sp >> finInit 
    task_cargasincrementales_sp >> finIncremental