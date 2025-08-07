import requests

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
