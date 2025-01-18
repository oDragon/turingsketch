import streamlit as st
import pyodbc
from dotenv import load_dotenv
import os

load_dotenv()

# Azure SQL Server configuration
DB_CONFIG = {
    'server': os.getenv('DB_SERVER'),
    'database': os.getenv('DB_NAME'),
    'username': os.getenv('DB_USERNAME'),
    'password': os.getenv('DB_PASSWORD'),
    'driver': '{ODBC Driver 17 for SQL Server}'
}


# Function to connect to the database
def get_db_connection():
    connection_string = (
        f"DRIVER={DB_CONFIG['driver']};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['username']};"
        f"PWD={DB_CONFIG['password']}"
    )

    return pyodbc.connect(connection_string)


# Function to delete the previous round (removes all existing rows)
def delete_previous_round():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Delete the existing rows in the table
        cursor.execute("DELETE FROM Drawings")
        
        connection.commit()
        cursor.close()
        connection.close()

        print("Previous round replaced successfully!")
    except Exception as e:
        st.error(f"Error deleting previous records: {e}")


# Function to upload new image (new round)
def upload_image_to_db(prompt1, image_data1):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Insert new prompts and images for the new round
        cursor.execute("""
            INSERT INTO drawings (prompt, picture) VALUES (?, ?);
        """, prompt1, image_data1)

        connection.commit()
        cursor.close()
        connection.close()

        print("New round uploaded successfully!")
    except Exception as e:
        st.error(f"Error uploading new round: {e}")


# Fetch all image and prompts from the Database
def fetch_images_from_db():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Fetch the images and prompts
        cursor.execute("SELECT prompt, picture FROM drawings")
        result = cursor.fetchall()

        cursor.close()
        connection.close()

        if result:
            return result
        else:
            return None
    except Exception as e:
        st.error(f"Error fetching images: {e}")
        return None


def is_first_player():
    """
    Returns True if the number of images in the database is NOT 1, else False.
    """
    if len(fetch_images_from_db()) is None or len(fetch_images_from_db()) != 1:
        return True
    else:
        return False