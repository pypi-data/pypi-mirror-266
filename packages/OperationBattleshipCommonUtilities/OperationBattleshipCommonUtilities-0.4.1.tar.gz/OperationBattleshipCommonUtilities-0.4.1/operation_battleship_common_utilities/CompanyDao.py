"""
This Python script defines a CompanyDao class that provides an interface for interacting with a PostgreSQL database that stores company data. The class includes methods for executing generic SQL commands, retrieving all companies, getting a company’s UUID by its LinkedIn URL, checking if a company exists in the database by its LinkedIn URL, and inserting new company data into the database. The script uses environment variables for secure database connection and includes logging for tracking operations and errors. The CompanyDao class is initialized with no arguments, and each method within the class serves a specific purpose related to the manipulation and retrieval of company data from the database. The script is designed to be used as a data access object in a larger application where company data needs to be stored and retrieved.

"""

import os
import uuid
from dotenv import load_dotenv
import pandas as pd
import psycopg2
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class CompanyDao:
    def __init__(self):
        logging.info(f"{self.__class__.__name__} class initialized")

    def genericSQL(sqlString):

        return


    """
    TODO: This function will need actual logic
    
    """
    def get_all_companies():

        companyDataFrame = []

        return companyDataFrame
    
    """
    When given a URL for the Company's LinkedIn Page, we want to get the UUID from the Companies Table. 
    """
    def getCompanyUuidByLinkedInUrl(self, companyLinkedinUrl):
        try:
            
            conn = psycopg2.connect(
                host=os.getenv("host"),
                database=os.getenv("database"),
                user=os.getenv("digitalOcean"),  
                password=os.getenv("password"),
                port=os.getenv("port")
            )
            cur = conn.cursor()
            
            cur.execute("SELECT company_id FROM Companies WHERE linkedin_url = %s", (companyLinkedinUrl,))
            
            rows = cur.fetchall()
            
            cur.close()
            conn.close()

            if rows:
                return rows[0][0]  
            else:
                logging.error(f"Error in getting Company ID. We always expect an ID in this function. Failed for: {companyLinkedinUrl} ")
                return None  

        except Exception as e:
            
            logging.error("Database connection error:", e)
            logging.error(f"Database error in CompanyDao.getCompanyUuidByLinkedInUrl for Company at: {companyLinkedinUrl} ")
            if 'conn' in locals():
                conn.close()
            return None
    
    """
    This function will check the company table and determine if this table contains any records with this company URL. 

    """
    def doesCompanyExist(self, linkedInCompanyUrl):
        
        conn = psycopg2.connect(
            host=os.getenv("host"),
            database=os.getenv("database"),
            user=os.getenv("digitalOcean"),
            password=os.getenv("password"),
            port=os.getenv("port")
            )
        try:

            cur = conn.cursor()
            
            cur.execute("SELECT * FROM companies WHERE linkedin_url = %s", (linkedInCompanyUrl, ))    
            
            rows = cur.fetchall()
            cur.close()
            conn.close()

            return len(rows) > 0

        except Exception as e:
            
            logging.error("Database connection error:", e)
            logging.error(f"Database error in CompanyDao.doesCompanyExist for Company at: {linkedInCompanyUrl} ")           
            
            if 'conn' in locals():
                conn.close()
            return False  
    

    def insertCompany(self, companyDataFrame):
        conn = None
        try:
            conn = psycopg2.connect(
                host=os.getenv("host"),
                database=os.getenv("database"),
                user=os.getenv("digitalOcean"),
                password=os.getenv("password"),
                port=os.getenv("port")
            )
            cur = conn.cursor()

            insert_sql = """
            INSERT INTO Companies (
                company_id, company_name, company_website, linkedin_url, industry, 
                num_employees, ownership_type, about_webpage, careers_page, 
                home_page_summary, about_page_summary, linkedin_company_summary, 
                has_datascience, has_product_operations
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            row = companyDataFrame.iloc[0].apply(lambda x: str(x) if isinstance(x, uuid.UUID) else x)
            cur.execute(insert_sql, tuple(row))

            conn.commit()

            cur.close()
            conn.close()

            return

        except Exception as e:
            logging.error("Database connection error:", e)
            logging.error(f"Database error in CompanyDao.insertCompany for Company at: {companyDataFrame["company_name"]} ")  
            if conn:
                conn.close()
            return
        
    def getCompanyNameByCompanyId(self, company_id):

        try:

            conn = psycopg2.connect(
                host=os.getenv("host"),
                database=os.getenv("database"),
                user=os.getenv("digitalOcean"),  
                password=os.getenv("password"),
                port=os.getenv("port")
            )
            
            cur = conn.cursor()
            
            cur.execute("SELECT company_name FROM Companies WHERE company_id = %s", (company_id,))
            
            rows = cur.fetchall()
            
            cur.close()
            conn.close()

            if rows:
                return rows[0][0]  
            else:
                logging.info(f"Error in getting Company Name. We always expect an name in this function. Failed for company id: {company_id} ")
                return None  

        except Exception as e:
            logging.error("Database connection error:", e)
            logging.error(f"Database error in CompanyDao.getCompanyNameByCompanyId for Company at: {company_id} ")
            
            if 'conn' in locals():
                conn.close()
            return None


    
