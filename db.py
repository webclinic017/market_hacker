#!/usr/bin/python
import psycopg2
from config import config
import pandas as pd

def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

	# close the communication with the PostgreSQL
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        if conn is not None:
            conn.close()
            print('Database connection closed.')
    return conn
def execute_mogrify(conn, df, table):
    """
    Using cursor.mogrify() to build the bulk insert query
    then cursor.execute() to execute the query
    """
    # Create a list of tupples from the dataframe values
    tuples = [tuple(x) for x in df.to_numpy()]
    # Comma-separated dataframe columns
    cols = ','.join(list(df.columns))
    # SQL quert to execute
    cursor = conn.cursor()
    values = [cursor.mogrify("(%s,%s,%s,%s,%s,%s,%s)", tup).decode('utf8') for tup in tuples]
    query  = "INSERT INTO %s(%s) VALUES " % (table, cols) + ",".join(values)
    
    try:
        cursor.execute(query, tuples)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    print("execute_mogrify() done")
    cursor.close()
def query(conn ,query):
    """
    Using cursor.mogrify() to build the bulk insert query
    then cursor.execute() to execute the query
    """
    cursor = conn.cursor()
     
    try:
        cursor.execute(query)
        cols = [x[0] for x in cursor.description]
        res = (cursor.fetchall())
        res = pd.DataFrame(res) 
        res.columns = cols
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    cursor.close()
    return res