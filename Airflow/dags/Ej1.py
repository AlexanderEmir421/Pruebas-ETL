from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
import datetime as dt
from Ej1.main import inicio
from Ej1.conn import get_engine_postgres
from Ej1.CargaIncremental import update_inactive,update_lastid
from Ej1.CargaInicial import set_inactive,set_lastid
from Ej1.CreateTables import cargar_csv

tablesG=[("dimdate", "dateid"),("dimcustomersegment", "segmentid"),("factsales", "salesid"),("dimproduct", "productid")]
tablesI=["dimdate","factsales"] #Tablas tecnica ultimo id (inserta apartir del ultimo id en mi tabla StgLog)
tablesE=["dimcustomersegment","dimproduct"]#Tablas tecnica estado (Hace un Full-refresh e identifica tablas borradas)

def cargaincremental_function(table, id):
    def call():
        engine =get_engine_postgres()
        if table in tablesI:
            update_lastid(table,id,engine)
        elif table in tablesE:
            update_inactive(table,id,engine)
    return call

def cargainicial_function(table, id):
    def call():
        engine = get_engine_postgres()
        if table in tablesI:
            set_lastid(table,id,engine)
        elif table in tablesE:
            set_inactive(table,id,engine)
    return call

#---------------------------------------------AIRFLOW------------------------------------------
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': dt.datetime(2025, 7, 19),
    'retries': 1,
    'retry_delay': dt.timedelta(minutes=5),
}

with DAG(
    'Ej1',
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