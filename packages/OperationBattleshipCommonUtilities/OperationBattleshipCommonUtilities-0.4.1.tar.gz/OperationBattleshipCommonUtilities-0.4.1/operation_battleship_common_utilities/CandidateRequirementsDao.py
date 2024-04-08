"""
This Python script is designed to interact with a PostgreSQL database to insert job candidate requirements data. It contains the CandidateRequirementsDao class, which has a method insertRequirementsForJobPosting.

The insertRequirementsForJobPosting method accepts a DataFrame containing multiple records of candidate requirements. Each record is inserted into the Candidate_Requirements table in the database. The method establishes a connection to the database using environment variables, prepares an SQL insert statement, and iterates over the DataFrame to insert each row into the database.

In case of any exceptions during the database operation, the method prints the error message and ensures the database connection is closed.

This script uses environment variables for sensitive data like the host, database name, user, password, and port, which should be stored in a .env file in the same directory. 
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


class CandidateRequirementsDao:
    def __init__(self):
        logging.info(f"{self.__class__.__name__} class initialized")

    def insertRequirementsForJobPosting(self, candidateRequirementsDataFrame):
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

            sql_insert_query = "INSERT INTO Candidate_Requirements (job_posting_id, unique_id, item) VALUES (%s, %s, %s)"

            for index, row in candidateRequirementsDataFrame.iterrows():

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