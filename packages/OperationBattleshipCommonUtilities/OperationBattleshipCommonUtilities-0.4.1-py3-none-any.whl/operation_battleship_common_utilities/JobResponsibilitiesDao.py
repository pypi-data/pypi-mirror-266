import os
from datetime import datetime
import uuid
import logging
from dotenv import load_dotenv
import pandas as pd
import psycopg2

load_dotenv('.env')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class JobResponsibilitiesDao :
    def __init__(self):
        logging.info(f"{self.__class__.__name__} class initialized")


    def insertJobResponsibilitiesForJobPosting(self, jobResponsibilitiesDataFrame):
        """
        When given a dataframe that has multiple records, this function will insert each record into the DB. 
        """

        conn = psycopg2.connect(
            host=os.getenv("host"),
            database=os.getenv("database"),
            user=os.getenv("digitalOcean"),
            password=os.getenv("password"),
            port=os.getenv("port")
        )
        try:
            cur = conn.cursor()

            sql_insert_query = "INSERT INTO Job_Responsibilities (job_posting_id, unique_id, item) VALUES (%s, %s, %s)"

            for index, row in jobResponsibilitiesDataFrame.iterrows():

                # Convert UUID to string before insertion
                job_posting_id_str = str(row['job_posting_id'])
                unique_id_str = str(row['unique_id'])
                data = (job_posting_id_str, unique_id_str, row['item'])
                cur.execute(sql_insert_query, data)
                
            conn.commit()

            cur.close()
            conn.close()

            return "Update successful!"

        except Exception as e:
            logging.error("Database connection error:", e)
            conn.close()
            return None
