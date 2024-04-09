from datetime import datetime
import os 
import pandas as pd
from google.cloud import bigquery
from lpb_lib import compute_log as log

def SQL_query(account_bigquery_secret, sql_path_folder, sql_path_file, last_execution_date = ""):
    """Execute a BigQuery SQL query and return the result as a DataFrame.
    Args:
    :account_bigquery_secret: The path to the JSON file containing the BigQuery credentials.
    :sql_path_folder: The path to the folder containing the SQL file to be executed.    
    :sql_path_file: The name of the SQL file to be executed.
    Returns:
        :df: A DataFrame containing the result of the SQL query.
    """
    sql_path = f"{sql_path_folder}/{sql_path_file}"
    with open(sql_path, "r") as file:
        sql = file.read()
    if last_execution_date != "":
        sql = sql.replace("WHERE date(updated_at) > DATE_SUB(CURRENT_DATE, INTERVAL 1 DAY)", f"WHERE date(updated_at) > DATE_SUB(\"{last_execution_date}\", INTERVAL 1 DAY)")
    
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = account_bigquery_secret
    client = bigquery.Client()
    df = client.query(sql).to_dataframe()
    header = "SQL_query"
    msg = f"{datetime.now()}\tExecution OK !\n{len(df)} lines returned\n{df.head(5)}"
    footer = "Fin de l'execution de la fonction"
    log.computelog(header, msg, footer)
    return df

def print_hello():
    """
    Ceci est une fonction de test pour afficher un message de bienvenue
    """
    print("Hello, le lib big_query est initiée !")