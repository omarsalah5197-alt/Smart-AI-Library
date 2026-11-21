import mysql.connector
from config import DB_CONFIG

def get_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)

        if connection.is_connected():
            return connection

    except mysql.connector.Error as error:
        print("Database Error:", error)

    return None
if __name__ == "__main__":
    db = get_connection()

    if db:
        print("MySQL Connected Successfully!")
        db.close()