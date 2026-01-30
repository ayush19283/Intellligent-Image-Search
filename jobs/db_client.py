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


def get_redis_client():
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    print("Connecting to Redis server...", REDIS_HOST, REDIS_PORT)
    redis_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
    return redis.from_url(redis_url)