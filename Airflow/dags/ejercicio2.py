from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from supabase import create_client
import requests
import pandas as pd
import datetime
import os


def normalizar(registro):
    if not registro.get('detalle'):
        return None
    detalle=registro['detalle'][0].copy()
    tipo_cambio=float(detalle['tipoCotizacion'])
    if tipo_cambio == 0:
        return None
    resultado={}
    resultado['moneda']=detalle['codigoMoneda']
    resultado['tipo_cambio']=tipo_cambio
    resultado['fecha'] = registro['fecha']
    return resultado

def loadsupabase(df,batch=10):
    supabase = create_client(os.getenv('URL_SUPABASE'), os.getenv('TOKEN_SUPABASE'))
    data = df.to_dict(orient="records")
    for i in range(0,len(data),batch):
        try:
            supabase.table("cotizaciones").insert(data[i:i+batch]).execute()
        except Exception as e:
            print(f"Error insertando en {e}")    

def get_api(fechadesde,fechahasta,moneda):
    try:
        url = f"https://api.bcra.gob.ar/estadisticascambiarias/v1.0/Cotizaciones/{moneda}"
        params = {
            'fechaDesde': fechadesde,
            'fechaHasta': fechahasta,
            'limit':50 #REDUCIMOS A 50 DATOS PARA NO SATURAR, SE PODRIA MEJORAR PARA TRAER TODOS LOS DATOS DISPONIBLES 
        }
        historial = requests.get(url, params=params, verify=False).json()['results']
        if historial != []:
            print(f"\n ANTES DE NORMALIZAR FECHA DESDE: {fechadesde} FECHA HASTA: {fechahasta}: \n {historial} \n")
            return [normalizado for datos in historial if(normalizado := normalizar(datos))] #NORMALIZA LOS DATOS PARA YA TENER PREPARADA LA TABLA
        else:
             return historial
    except Exception as e:
        print(f"Error en la Api {moneda}: {e}")
        return []

def cargaincremental():
    fechahasta = datetime.date.today().strftime('%Y-%m-%d')
    supabase = create_client(os.getenv('URL_SUPABASE'), os.getenv('TOKEN_SUPABASE'))
    url_divisas = "https://api.bcra.gob.ar/estadisticascambiarias/v1.0/Maestros/Divisas"
    divisas = requests.get(url_divisas, verify=False).json()['results']
    for i,moneda in (pd.DataFrame(divisas).head(10).iterrows()):#AUMENTAMOS A LAS PRIMERAS 10 MONEDAS PARA VER SI LA CARGA INCREMENTAL AUMENTO AÑADIENDO NUEVAS MONEDAS
        fecha_desde=(supabase.table('cotizaciones')
                    .select("fecha")
                    .eq("moneda",moneda['codigo'])
                    .order("fecha",desc=True)
                    .limit(1)
                    .execute()
        )
        if fecha_desde.data:
            ultimafecha = fecha_desde.data[0]['fecha']  
            fechadesde = (datetime.datetime.strptime(ultimafecha, '%Y-%m-%d').date() + datetime.timedelta(days=1)) 
            print(f"FECHA DESDE: {ultimafecha} MONEDA {moneda['codigo']} NUEVA CONSULTA DESDE:{fechadesde} HASTA {fechahasta}\n")
        else:
            fechadesde=datetime.date.today() - datetime.timedelta(days=30),
            print(f"NO HAY DATOS DE ESTA MONEDA {moneda['codigo']} INTENTADO TRAER DATOS NUEVOS...\n")
        historial=get_api(fechadesde,fechahasta,moneda['codigo'])
        loadsupabase(pd.DataFrame(historial))

def cargainicial():
    fechadesde=datetime.date.today() - datetime.timedelta(days=30),
    fechahasta=datetime.date.today() - datetime.timedelta(days=1),
    url_divisas = "https://api.bcra.gob.ar/estadisticascambiarias/v1.0/Maestros/Divisas"
    divisas = requests.get(url_divisas, verify=False).json()['results']
    for i,moneda in (pd.DataFrame(divisas).head(5).iterrows()):#SOLO 5 MONEDAS PARA NO SATURAR
        historial=get_api(fechadesde,fechahasta,moneda['codigo'])
        print(f"\n Normalizado {historial}\n")
        loadsupabase(pd.DataFrame(historial))

def inicio():
    supabase = create_client(os.getenv('URL_SUPABASE'), os.getenv('TOKEN_SUPABASE'))
    cotizaciones=supabase.table("cotizaciones").select("*").execute()
    print(f"\n ----------------------\n{cotizaciones}")
    if cotizaciones.data != []:
       return 'cargaincremental'
    else:
        return 'cargainicial'
    

#------------------------------------------------AIRFLOW-----------------------------------------------
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.datetime(2025, 7, 19),
    'retries': 1,
    'retry_delay': datetime.timedelta(minutes=5),
}

with DAG(
    'Ejercicio2',
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