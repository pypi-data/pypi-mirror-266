"""
This script is intended to be the only class that actually calls the PostGres DB. All other DAO Classes will reference this Class. 

TODO: Implement this class and update other scripts to call this instead. 

"""

import os
from datetime import datetime
import uuid
import logging
from dotenv import load_dotenv
import pandas as pd
import psycopg2

load_dotenv('.env')


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GenaricDatabaseDao:
    def __init__(self):
        logging.info(f"{self.__class__.__name__} class initialized")

    def execute_select_command(self, sql_statement):
        conn = psycopg2.connect(
            host=os.getenv("host"),
            database=os.getenv("database"),
            user=os.getenv("digitalOcean"),
            password=os.getenv("password"),
            port=os.getenv("port")
            )
        try:
            cur = conn.cursor()
            
            cur.execute(sql_statement)

            rows = cur.fetchall()

            df = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])

            cur.close()
            conn.close()

            return df

        except Exception as e:
            logging.error("Database error:", e)
            conn.close()
            return None
    
    def execute_update_command(sql_statement, data):

        return
    
    def execute_insert_command(sql_statement, data):

        return