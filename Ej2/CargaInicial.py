import datetime
import requests
import pandas as pd
from Ej2.LoadSupabase import loadsupabase
from Ej2.get_api import get_api

def cargainicial():
    fechadesde=datetime.date.today() - datetime.timedelta(days=30),
    fechahasta=datetime.date.today() - datetime.timedelta(days=1),
    url_divisas = "https://api.bcra.gob.ar/estadisticascambiarias/v1.0/Maestros/Divisas"
    divisas = requests.get(url_divisas, verify=False).json()['results']
    for i,moneda in (pd.DataFrame(divisas).head(5).iterrows()):#SOLO 5 MONEDAS PARA NO SATURAR
        historial=get_api(fechadesde,fechahasta,moneda['codigo'])
        print(f"\n Normalizado {historial}\n")
        loadsupabase(pd.DataFrame(historial))
