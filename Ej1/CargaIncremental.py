import pandas as pd
from Ej1.conn import get_client_supabase
from Ej1.LoadSupabase import get_staging_table_name,load_supabase,set_lastid_logs,set_stanging

#dectecta si un dato se elimino comparando tablas
def update_inactive(table,id,engine):
    stanging=get_staging_table_name(table)
    df= pd.read_sql(f'SELECT * FROM "{table}"',engine)
    supabase = get_client_supabase()
    supabase= supabase.table(stanging).select("*").execute()
    df_supabase = pd.DataFrame(supabase.data)
    
    if not df_supabase.empty:
        comparison = df.merge(df_supabase,on=[id],how='outer',indicator=True,suffixes=('_PG', '_SP'))
        print(f"\n ---------------FULL OTHER JOIN-------------\n {comparison}\n")
        # Renombrar columnas que terminan en '_PG' les quitamos el sufijo
        rename_pg_cols = {col: col[:-3] for col in comparison.columns if col.endswith('_PG')}
        # Eliminar columnas que terminan en '_SP'
        drop_sp_cols = [col for col in comparison.columns if col.endswith('_SP')]
        
        new_customers = (comparison[comparison["_merge"] == 'left_only']
                        .copy()
                        .assign(state="active")
                        .rename(columns=rename_pg_cols)
                        .drop(['_merge'] + drop_sp_cols, axis=1)
        )
        print(f"\n ---------------Nuevos Datos-------------\n {new_customers}\n")
        #estos son elementos borrados de la tabla origen
        condicion = ((comparison["_merge"] == 'right_only') &(comparison["state"] != "inactive"))
        delete_customers = (comparison[condicion]
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
        load_supabase(stanging,df.assign(state="active"))
        load_supabase(table,df)
        last_id=df[id].max()
        set_lastid_logs(table,last_id)
        
#Carga apartir del ultimo id 
def update_lastid(table,id,engine):
    supabase = get_client_supabase()
    result = supabase.table("stg_log").select("last_id").eq("table_name", table).execute()
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
