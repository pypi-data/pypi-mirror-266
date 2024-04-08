import os
from datetime import datetime
import uuid
import logging
from dotenv import load_dotenv
import pandas as pd
import psycopg2

load_dotenv('.env')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class JobPostingDao:
    def __init__(self):
        logging.info(f"{self.__class__.__name__} class initialized")

    def execute_db_command(sql_statement, data):

        return
    
    
    def getAllDataScienceOrProductCategorizedJobs(self):
        """
        This function calls the Job Posting Table to find all the records that have a job_category of Data Science or Product
        Returns the list as a Pandas Dataframe
        
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
            
            cur.execute("SELECT * FROM job_postings WHERE job_category IN ('Product_Management', 'Data_Science')")

            rows = cur.fetchall()

            df = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])

            cur.close()
            conn.close()

            return df

        except Exception as e:
            logging.error("Database connection error:", e)
            logging.error(f"Database error in JobPosting.getAllDataScienceOrProductCategorizedJobs(). ")  
            conn.close()
        return

    def getAllProductManagerJobs(self):
        """
        This fuction calls the Job Posting Table to find all the records that contain either AI or Product Manager in the title.  
    
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
            cur.execute("SELECT * FROM job_postings WHERE (job_title ILIKE '%AI%' OR job_title ILIKE '%Product Manager%')")

            rows = cur.fetchall()

            df = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])

            cur.close()
            conn.close()

            return df

        except Exception as e:
            logging.error("Database connection error:", e)
            logging.error(f"Database error in JobPosting.getAllProductManagerJobs. ")  
            conn.close()
        return
    
    """
    This method will update the given LinkedIn Job Posting with today's date for most recent updated date. 
    """
    def updateLinkedInJobRecordUpdatedDate(self, jobUrl):
         # Establish a connection to the database
        conn = psycopg2.connect(
            host=os.getenv("host"),
            database=os.getenv("database"),
            user=os.getenv("digitalOcean"),
            password=os.getenv("password"),
            port=os.getenv("port")
        )
        try:
            cur = conn.cursor()
            
            # Code to construct a SQL query from the job_posting dataframe
            # Assuming job_posting is a single record from your DataFrame
            sql_update_query = """
            UPDATE job_postings
            SET job_last_collected_date = %s
            WHERE posting_url = %s;
            """
            todaysDate = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M:%S'), 
            data = (todaysDate, jobUrl)
            
            cur.execute(sql_update_query, data)
            
            conn.commit()

            cur.close()
            conn.close()

            return "Update successful!"

        except Exception as e:
            logging.error("Database connection error:", e)
            conn.close()
            return None
    
    def update_job_posting(self, job_posting):
 
        # Dynamically build the SET part of the SQL statement
        set_sql = ', '.join([f"{col} = %s" for col in job_posting.index if col != 'job_posting_id'])

        # Create the SQL statement
        sql_update_query = f"""
        UPDATE job_postings
        SET {set_sql}
        WHERE job_posting_id = %s;
        """

        # Prepare data tuple to be updated (exclude job_posting_id and append it at the end for the WHERE clause)
        data = tuple(job_posting[col] for col in job_posting.index if col != 'job_posting_id') + (job_posting['job_posting_id'],)

        # Establish a connection to the database
        try:
            conn = psycopg2.connect(
                host=os.getenv("host"),
                database=os.getenv("database"),
                user=os.getenv("digitalOcean"),  
                password=os.getenv("password"),
                port=os.getenv("port")
            )

            # Use a context manager to handle the cursor's opening and closing
            with conn:
                with conn.cursor() as cur:
                    # Execute the SQL query
                    cur.execute(sql_update_query, data)

            # Logging and return message
            logging.info("Update successful for job_posting_id: %s", job_posting['job_posting_id'])
            return "Update successful!"

        except Exception as e:
             # Log the error along with the SQL query and data
            logging.error("Database connection error: %s. SQL: %s, Data: %s", e, sql_update_query, data)
            # Optionally, you might want to format the SQL string to replace placeholders with actual data for clearer logging
            try:
                formatted_sql = cur.mogrify(sql_update_query, data).decode("utf-8")
                logging.error("Formatted SQL sent to DB: %s", formatted_sql)
            except Exception as mogrify_error:
                logging.error("Error formatting SQL: %s", mogrify_error)

        finally:
            
            if conn is not None:
                conn.close()

    
    def fetchPmJobsRequiringEnrichment(sef):
        """
        This fuction calls the Job Posting Table to find all the PM records that need further enrichment. 
        This process adds salary details, AI Details and basic job description info. 
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
            
            cur.execute("SELECT * FROM job_postings WHERE (job_title ILIKE '%AI%' OR job_title ILIKE '%Product Manager%') AND is_ai IS NULL order by job_posting_date desc;")

            rows = cur.fetchall()

            df = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])

            cur.close()
            conn.close()

            return df

        except Exception as e:
            logging.error("Database connection error:", e)
            logging.error(f"Database error in JobPosting.getUnprocessedAiClassificationJobs. ")  
            conn.close()
            return None


    def fetchJobsRequiringEnrichment(self):
        """
        This fuction calls the Job Posting Table to find all the records that need further enrichment. 
        This process adds salary details, AI Details and basic job description info. 
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
            
            cur.execute("SELECT * FROM job_postings WHERE is_ai IS NULL")

            rows = cur.fetchall()

            df = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])

            cur.close()
            conn.close()
            return df

        except Exception as e:
            logging.error("Database connection error:", e)
            logging.error(f"Database error in JobPosting.fetchJobsRequiringEnrichment(). ")  
            conn.close()
            return None
    
    def checkIfJobExists(self, cleanedLinkedInJobURL):
        try:
            conn = psycopg2.connect(
                host=os.getenv("host"),
                database=os.getenv("database"),
                user=os.getenv("digitalOcean"),  
                password=os.getenv("password"),
                port=os.getenv("port")
            )
            cur = conn.cursor()

            sql_command = "SELECT * FROM job_postings WHERE posting_url = %s"
            
            cur.execute(sql_command, (cleanedLinkedInJobURL, ))
            
            rows = cur.fetchall()

            cur.close()
            conn.close()

            return len(rows) > 0

        except Exception as e:
            
            logging.error("Database connection error:", e)
            logging.error(f"Database error in JobPosting.checkIfJobExists for Job at: {cleanedLinkedInJobURL} ")  
            
            mogrified_query = cur.mogrify(sql_command, (cleanedLinkedInJobURL, )).decode('utf-8')
            logging.error(f"Error occurred while Executing SQL command: {mogrified_query}")
           
            if 'conn' in locals():
                conn.close()
            return False  
        

    def insertNewJobRecord(self, jobpostingDataFrame):

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

            # SQL statement for inserting data
            insert_sql = """INSERT INTO job_postings (
                job_posting_id, company_id, posting_url, posting_source, posting_source_id, job_title,
                 full_posting_description, job_description, is_ai, job_salary, job_posting_company_information, 
                 job_posting_date, job_insertion_date, job_last_collected_date, job_active, city, state
            ) Values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            # Assuming there's only one row in the DataFrame, access the first row directly
            # Convert the UUID to a string if the column is expected to be a UUID
            row = jobpostingDataFrame.iloc[0].apply(lambda x: str(x) if isinstance(x, uuid.UUID) else x)
            
            # Log the SQL statement and data. We can uncomment the log file line below when we want more verbose logging. 
            #logging.info(f"Executing SQL: {insert_sql} with data: {tuple(row)}")

            cur.execute(insert_sql, tuple(row))
            conn.commit()

            # Close the cursor and connection
            cur.close()
            conn.close()
            return 1

        except Exception as e:
            # Log or print the error for debugging

            logging.error(f"Database error: {e}")
            logging.error(f"Database error in JobPosting.insertNewJobRecord for Job at: {jobpostingDataFrame["posting_url"]} ")
            logging.error(f"Executing SQL: {insert_sql} with data: {tuple(row)}")  
            
            if conn:
                conn.close() 
            
            return -1
        
    def getAllJobs(self):
        """
        This fuction calls the Job Posting Table to find all the records and returns them to the user as a pandas pd 
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
            
            cur.execute("SELECT * FROM job_postings")

            rows = cur.fetchall()

            df = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])

            cur.close()
            conn.close()

            return df

        except Exception as e:
            logging.error("Database connection error:", e)
            logging.error(f"Database error in JobPosting.getUnprocessedAiClassificationJobs. ")  
            conn.close()
            return None
        
    def getActiveJobsIdsAsDataFrame(self):
        """
        This fuction calls the Job Posting Table to find all the records where active = true 
        and returns them to the user as a pandas pd 
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
            
            cur.execute("SELECT * FROM job_postings where job_active = true")

            rows = cur.fetchall()

            df = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])

            cur.close()
            conn.close()

            return df

        except Exception as e:
            logging.error("Database connection error:", e)
            logging.error(f"Database error in JobPosting.getActiveJobsIdsAsDataFrame. ")  
            conn.close()
            return None
    
    def getJobByJobPostingId(self, job_posting_id):
        """
        This fuction calls the Job Posting Table to find the record by a given job_posting_id and returns it as a pandas pd 
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
            
            sql_command = "SELECT * FROM job_postings where job_posting_id = %s"
            cur.execute(sql_command, (job_posting_id, ))

            rows = cur.fetchall()

            df = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])

            cur.close()
            conn.close()

            return df

        except Exception as e:
            logging.error("Database connection error:", e)
            logging.error(f"Database error in JobPosting.getJobByJobPostingId. ")  
            conn.close()
            return None

    
    def getProductManagerJobs(self):

        return
    
    def getUncategorizedJobs(self):
        
        """
        This fuction calls the Job Posting Table to find all the PM records that need further enrichment. 
        This process adds salary details, AI Details and basic job description info. 
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
            
            cur.execute("SELECT * FROM job_postings WHERE job_category is null;")

            rows = cur.fetchall()

            df = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])

            cur.close()
            conn.close()


            return df

        except Exception as e:
            logging.error("Database connection error:", e)
            logging.error(f"Database error in JobPosting.getUnprocessedAiClassificationJobs. ")  
            conn.close()
            return None

    
    def getjobsFromListOfJobsIds(self, dataframeOfJobIds):
        """
        Purpose: When given a list of Job_Ids, this function will call the job_postings table and return the list of jobs that match the given IDs. 

        Args:
            dataframeOfJobIds: Pandas Dataframe where one column contains 'id' and this corresponds to job_posting_id in the Postgres DB

        Return Value:
            Pandas Dataframe of each job record, company name and aother associated metadata.  
        """
        job_ids = dataframeOfJobIds['job_posting_id'].tolist()

        job_ids_tuple = tuple(job_ids)

        sql_query = f"""
        SELECT
            c.company_name,
            c.linkedin_url,
            jp.job_title,
            jp.posting_url,
            jp.full_posting_description,
            jp.job_description,
            jp.is_ai,
            jp.is_genai,
            jp.salary_low,
            jp.salary_midpoint,
            jp.salary_high,
            jp.job_salary,
            jp.job_category,
            jp.job_posting_date,
            jp.job_posting_id AS job_posting_id,
            jp.company_id,
            jp.posting_source,
            jp.posting_source_id,
            jp.job_posting_company_information,
            jp.job_insertion_date,
            jp.job_last_collected_date,
            jp.job_active,
            jp.city,
            jp.state,
            jp.job_skills,
            jp.is_ai_justification,
            jp.work_location_type
        FROM
            job_postings jp
        JOIN
            companies c ON jp.company_id = c.company_id
        WHERE
            jp.job_posting_id IN %s;
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

            cur.execute(sql_query, (job_ids_tuple,))

            rows = cur.fetchall()

            if rows:
                df = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])
            else:
                df = pd.DataFrame()

            cur.close()
            conn.close()

            return df

        except Exception as e:
            logging.error("Database connection error:", e)
            conn.close()
            return pd.DataFrame()
