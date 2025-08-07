import pandas as pd 
from Ej1.LoadSupabase import get_staging_table_name,load_supabase,set_lastid_logs

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

def set_inactive(table,id,engine):
    stanging=get_staging_table_name(table)
    df= pd.read_sql(f'SELECT * FROM "{table}"',engine)
    print(f"\n --------------\n {df} \n --------------\n")
    df_state = df.assign(state='active')
    load_supabase(stanging,df_state)
    load_supabase(table,df) 
    last_id_supabase = df[id].max()
    set_lastid_logs(table, last_id_supabase)

