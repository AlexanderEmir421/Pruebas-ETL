from Ej2.conn import get_client_supabase
def inicio():
    supabase = get_client_supabase()
    cotizaciones=supabase.table("cotizaciones").select("*").execute()
    print(f"\n ----------------------\n{cotizaciones}\n------------------------")
    if cotizaciones.data != []:
       return 'cargaincremental'
    else:
        return 'cargainicial'