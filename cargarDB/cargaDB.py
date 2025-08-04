from supabase import create_client
from datetime import datetime
import os
from sqlalchemy import create_engine
import pandas as pd

url = os.getenv('URL_SUPABASE')
key = os.getenv('TOKEN_SUPABASE')
supabase = create_client(url, key)
data = supabase.table("StgLogs").select("*").execute()

#fecha=datetime.now()

fecha="2025-07-01 22:34:40.597862"

engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRESPORT')}/{os.getenv('POSTGRES_DB')}"
)

def load_sp(table,df,batch=10):
    df = df.drop(columns=['index'])
    data = df.to_dict(orient="records")
    for i in range(0,len(data),batch):
        try:
            supabase.table(table).insert(data[i:i+batch]).execute()
            print(f"""---------------------------------------datos insertados------------------------\n 
                {df} \n ------------------------------------------------------------------------------\n""")
        except Exception as e:
            print(f"Error insertando en {table}: {e}")
            
def set_customer(df):
    df = df.drop(columns=['index'])
    for index,row in df.iterrows(): 
        supabase.table("StgCustomer").update({
            "state":row["state"]
        }).eq("Segmentid",row["Segmentid"]).execute()

def set_lastid_logs(name_table,last_id):
    supabase.table("StgLogs").update({
        "last_id":last_id
    }).eq("table_name",name_table).execute()
    
def get_inactive_Customers(df):
    Customer= supabase.table("StgCustomer").select("*").execute()
    df_customers = pd.DataFrame(Customer.data)
    comparison = df.merge(df_customers,on=['Segmentid'],how='outer',indicator=True,suffixes=('_PG', '_SP'))
    #todos estos son los datos nuevos a guardar
    new_customers=(comparison[comparison["_merge"] == 'left_only']
                 .copy()
                 .assign(state="active")
                 .rename(columns={'City_PG':'City'})  
                 .drop(['_merge','City_SP'], axis=1))
    #estos son elementos borrados de la tabla origen
    condicion = (
        (comparison["_merge"] == 'right_only') & 
        (comparison["state"] != "inactive")
    )
    delete_customers=(comparison[condicion]                      
                      .copy()
                      .assign(state="inactive")
                      .rename(columns={'City_SP':'City'})
                      .drop(['_merge','City_PG'],axis=1)
                      )
    load_sp("StgCustomer",new_customers)
    load_sp("DimCustomerSegment",new_customers)
    set_customer(delete_customers) 
    
def set_lastid(table, cond):
    result = supabase.table("StgLogs").select("last_id").eq("table_name", table).execute()
    last_id = result.data[0].get('last_id')
    
    if last_id is not None:
        if table == "FactSales":
            df = pd.read_sql(f'SELECT * FROM "{table}" WHERE "{cond}" > \'{last_id}\'', engine)
        else:
            last_id = int(last_id)
            df = pd.read_sql(f'SELECT * FROM "{table}" WHERE "{cond}" > {last_id}', engine)
    else:
        df = pd.read_sql(f'SELECT * FROM "{table}"', engine)
    
    if not df.empty:
        last_id = df[cond].max()
        last_id_supabase = str(last_id)
        load_sp(table, df)
        set_lastid_logs(table, last_id_supabase)
    else:
        print("Datos no encontrados manteniendo ultimo id")
        
        
#CAMBIAR LOGICA SI LA FECHA ES 1+ DIA HACER LA CONSULTAS O SI LA TABLA NUNCA SE CREO
if len(data.data) != 0:
    tables=["DimDate","DimCustomerSegment","DimProduct","FactSales"]
    for i in tables:
        if i == "DimDate":
            set_lastid(i,"dateid")
        elif i == "DimCustomerSegment":
            df= pd.read_sql("SELECT * FROM DimCustomerSegment",engine)
            get_inactive_Customers(df)
        elif i == "DimProduct":
            set_lastid(i,"Productid")
        else:
            set_lastid(i,"Salesid")
else:
    pass
