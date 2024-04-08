import os
import logging
from dotenv import load_dotenv
import pandas as pd
import psycopg2

load_dotenv('.env')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class JobSkillsDao :
    def __init__(self):
        logging.info(f"{self.__class__.__name__} class initialized")


    def insertSkillsForJobPosting(self, jobSkillsDataFrame):
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

            sql_insert_query = "INSERT INTO Job_Skills (job_posting_id, unique_id, item) VALUES (%s, %s, %s)"

            for index, row in jobSkillsDataFrame.iterrows():

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
        

    def getSkillsForJobID(self, job_posting_id):

        """
        This function calls the Job Skills Table to find all the records that have the given job_posting_id 
        
        Returns the list as a Pandas DataFrame
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
            
            sql_select_query = "SELECT * FROM job_skills WHERE job_posting_id = %s"
            cur.execute(sql_select_query, (job_posting_id,))  

            rows = cur.fetchall()

            if rows:
                df = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])
            else:
                df = pd.DataFrame()

            cur.close()
            conn.close()

            return df

        except Exception as e:
            logging.error(f"Database connection error in getSkillsForJobID: {e}")
            conn.close()
            return pd.DataFrame()  
        
