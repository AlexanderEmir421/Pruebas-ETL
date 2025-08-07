from supabase import create_client
from sqlalchemy import create_engine
import psycopg2
import os

def get_engine_postgres():
    return create_engine(
        f"postgresql+psycopg2://{os.getenv('POSTGRES_USUARIO')}:{os.getenv('POSTGRES_PASSWORD_USUARIO')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB_REPLICA')}"
    )

def get_client_supabase():
    return create_client(os.getenv('URL_SUPABASE'), os.getenv('TOKEN_SUPABASE'))
    
def get_postgres_conn():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        dbname=os.getenv("POSTGRES_DB_REPLICA"),
        user=os.getenv("POSTGRES_USUARIO"),
        password=os.getenv("POSTGRES_PASSWORD_USUARIO"),
        port=os.getenv("POSTGRES_PORT")
    )
    
    
    
    