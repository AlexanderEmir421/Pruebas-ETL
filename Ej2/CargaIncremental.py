import datetime 
import requests
import pandas as pd
from Ej2.LoadSupabase import loadsupabase
from Ej2.conn import get_client_supabase
from Ej2.get_api import get_api

def cargaincremental():
    fechahasta = datetime.date.today().strftime('%Y-%m-%d')
    supabase = get_client_supabase()
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
