from Ej2.conn import get_client_supabase

def loadsupabase(df,batch=10):
    supabase = get_client_supabase()
    data = df.to_dict(orient="records")
    for i in range(0,len(data),batch):
        try:
            supabase.table("cotizaciones").insert(data[i:i+batch]).execute()
        except Exception as e:
            print(f"Error insertando en {e}")    
