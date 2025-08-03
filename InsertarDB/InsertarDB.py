from sqlalchemy import create_engine, text
import os 
import pandas as pd
import glob

engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRESPORT')}/{os.getenv('POSTGRES_DB')}"
)

def load_csv():
    files=glob.glob("csv/*.csv")
    for f in files:
        try:    
            df=pd.read_csv(f)
            table_name = os.path.splitext(os.path.basename(f))[0].lower()
            df.to_sql(table_name,engine,schema=None,if_exists='replace')
        except Exception as e:
            print(f"ERROR: {e}")
            
if __name__== "__main__":
    load_csv()