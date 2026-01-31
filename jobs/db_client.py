import os
import re
import redis
import psycopg2
import psycopg2.extras



def get_conn():
    # Get config from environment
    conn = psycopg2.connect(
        os.getenv("DSN")
    )
    
    # Create cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    return conn, cur

