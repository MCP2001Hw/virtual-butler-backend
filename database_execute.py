import mysql.connector
from mysql.connector import Error
import datetime

def execute_SQL(query, params=None):
    try:
        # Establish the database connection
        mydb = mysql.connector.connect(
            host="",
            port=1,
            user="",
            password="",
            database=""
        )

        cursor = mydb.cursor()

        # Execute the query with or without parameters
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        # If the query is a SELECT statement, fetch and return the results
        if query.strip().lower().startswith("select"):
            results = cursor.fetchall()
            return results if results else None
        
        # Commit the transaction for non-SELECT statements
        mydb.commit()
        timestamp = datetime.datetime.now()
        print(f"Commit successful! {timestamp}")
        return cursor.rowcount

    except Error as e:
        print(f"Database Error: {e}")
        return None

    finally:
        # Close the cursor and database connection
        if 'cursor' in locals():
            cursor.close()
        if 'mydb' in locals():
            mydb.close()