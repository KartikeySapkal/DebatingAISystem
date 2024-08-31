import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
import os
from contextlib import contextmanager

# Load database configuration from environment variables
DB_CONFIG = {
    'dbname': os.environ.get('DB_NAME'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'host': os.environ.get('DB_HOST'),
    'port': os.environ.get('DB_PORT', 5432)
}

# Create a connection pool
connection_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    **DB_CONFIG
)


class DatabaseError(Exception):
    """Custom exception for database-related errors"""
    pass


@contextmanager
def get_db_connection():
    """
    Context manager for database connections.
    Yields a connection from the pool and ensures it's returned when done.
    """
    connection = None
    try:
        connection = connection_pool.getconn()
        yield connection
    except psycopg2.Error as e:
        raise DatabaseError(f"Database error: {str(e)}")
    finally:
        if connection:
            connection_pool.putconn(connection)


@contextmanager
def get_db_cursor(commit=False):
    """
    Context manager for database cursors.
    Yields a cursor and optionally commits changes.
    """
    with get_db_connection() as connection:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        try:
            yield cursor
            if commit:
                connection.commit()
        except psycopg2.Error as e:
            connection.rollback()
            raise DatabaseError(f"Database error: {str(e)}")
        finally:
            cursor.close()


def execute_query(query, params=None, fetch=False, commit=False):
    """
    Execute a database query.
    :param query: SQL query string
    :param params: Parameters for the query
    :param fetch: If True, fetch and return results
    :param commit: If True, commit the transaction
    :return: Query results if fetch is True, else None
    """
    with get_db_cursor(commit=commit) as cursor:
        cursor.execute(query, params)
        if fetch:
            return cursor.fetchall()


def execute_many(query, params_list, commit=True):
    """
    Execute a query many times with different parameters.
    :param query: SQL query string
    :param params_list: List of parameter tuples
    :param commit: If True, commit the transaction
    """
    with get_db_cursor(commit=commit) as cursor:
        cursor.executemany(query, params_list)


# Example usage functions

def get_user(username):
    """Fetch a user from the database"""
    query = "SELECT * FROM users WHERE username = %s"
    results = execute_query(query, (username,), fetch=True)
    return results[0] if results else None


def create_user(username, password_hash):
    """Create a new user in the database"""
    query = "INSERT INTO users (username, password) VALUES (%s, %s)"
    execute_query(query, (username, password_hash), commit=True)


def save_debate_scores(username, user_scores, ai_scores, plot_json):
    """Save debate scores to the database"""
    query = """
    INSERT INTO debate_scores (username, user_scores, ai_scores, plot_json)
    VALUES (%s, %s, %s, %s)
    """
    execute_query(query, (username, user_scores, ai_scores, plot_json), commit=True)


# Add more database operation functions as needed

# Cleanup function to be called when the application shuts down
def close_db_pool():
    if connection_pool:
        connection_pool.closeall()
    print("Database connection pool closed.")
