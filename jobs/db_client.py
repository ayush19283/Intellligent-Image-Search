import os
import psycopg2
import psycopg2.extras



def get_conn():
    # Get config from environment
    dsn = os.getenv("DSN")
    print(dsn)
    if not dsn:
        raise ValueError("DSN environment variable is not set.")
    

    conn = psycopg2.connect(
        dsn
    )
    
    # Create cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    return conn, cur

