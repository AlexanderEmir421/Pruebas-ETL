from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.empty import EmptyOperator
import datetime
from Ej2.main import inicio
from Ej2.CargaInicial import cargainicial    
from Ej2.CargaIncremental import cargaincremental

#------------------------------------------------AIRFLOW-----------------------------------------------
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.datetime(2025, 7, 19),
    'retries': 1,
    'retry_delay': datetime.timedelta(minutes=5),
}

with DAG(
    'Ej2',
    default_args=default_args,
    description='Extraer datos de la api BRCA',
    schedule_interval='0 0 * * 1',#Ejecucion semanal cada lunes a las 00;00
    catchup=False,
) as dag:
    
    inicio=BranchPythonOperator(
        task_id='Inicio',
        python_callable=inicio
    )
    
    inicial=PythonOperator(
        task_id='cargainicial',
        python_callable=cargainicial
    )
    
    incremental=PythonOperator(
        task_id='cargaincremental',
        python_callable=cargaincremental
    )
    
    fin = EmptyOperator(
        task_id='fin',
        trigger_rule='none_failed'
    )
    
    inicio >> [inicial, incremental]
    [inicial, incremental] >> fin 