#!/usr/bin/python
import psycopg2
from psycopg2 import pool
from config import config
import pandas as pd
postgreSQL_pool = ""
def putback_conn(conn):
    global postgreSQL_pool
    if(postgreSQL_pool != ""):
        postgreSQL_pool.putconn(conn)
def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        global postgreSQL_pool
        params = config()
        if(postgreSQL_pool == ""):
            postgreSQL_pool = psycopg2.pool.SimpleConnectionPool(1, 20,**params)
        
            print("Connection pool created successfully")
        conn = postgreSQL_pool.getconn()
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
        print("execute_mogrify() done")    
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
    finally:
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