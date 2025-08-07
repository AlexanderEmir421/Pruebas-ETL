from Ej1.conn import get_client_supabase
import datetime as dt

def get_staging_table_name(table):
    return f"stg_{table}"

def set_lastid_logs(name_table,last_id):
    fecha_actual_utc = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S+00')
    supabase = get_client_supabase()
    supabase.table("stg_log").update({
        "last_id":str(last_id),
        "last_load":fecha_actual_utc
    }).eq("table_name",name_table).execute()

def load_supabase(table,df,batch=10):
    supabase = get_client_supabase()
    data = df.to_dict(orient="records")
    for i in range(0,len(data),batch):
        try:
            supabase.table(table).insert(data[i:i+batch]).execute()
            print(f"---------------------------------------Datos insertados Correctamente------------------ \n {df}\n ")
        except Exception as e:
            print(f"Error insertando en {table}: {e}")


def set_stanging(table,id,df):
    supabase = get_client_supabase()
    for index,row in df.iterrows(): 
        supabase.table(table).update({
            "state":row["state"]
        }).eq(id,row[id]).execute()
