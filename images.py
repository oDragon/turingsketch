import streamlit as st
import pyodbc
from io import BytesIO
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

        st.success("Previous round replaced successfully!")
    except Exception as e:
        st.error(f"Error deleting previous round: {e}")


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

        st.success("New round uploaded successfully!")
    except Exception as e:
        st.error(f"Error uploading new round: {e}")


# Fetch Image and Prompt from the Database
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
    if len(fetch_images_from_db()) != 1:
        return True
    else:
        return False

# Streamlit Interface
st.title("AI vs Human Drawings")

# Input for the two prompts and file uploaders for the images
prompt1 = st.text_input("Enter the first prompt for your drawing:")
prompt2 = st.text_input("Enter the second prompt for your drawing:")
uploaded_file1 = st.file_uploader("Upload the first drawing image", type=["png", "jpg", "jpeg"])
uploaded_file2 = st.file_uploader("Upload the second drawing image", type=["png", "jpg", "jpeg"])

# If the "Upload New Round" button is clicked (button is created in-line)
if st.button("Upload New Round"):
    if prompt1 and prompt2 and uploaded_file1 and uploaded_file2:
        delete_previous_round()

        # Convert the images to binary data
        image_data1 = uploaded_file1.read()

        # Upload the new round's images and prompts
        upload_image_to_db(prompt1, image_data1)
    else:
        st.error("Please provide both prompts and upload both images.")

# If the "Fetch New Round" button is clicked (button is created in-line)
# Fetch the uploaded images and prompts 
if st.button("Fetch New Round"):
    # Fetch the images and prompts for the most recent round 
    images_and_prompts = fetch_images_from_db()
    if images_and_prompts:
        for i, (prompt, image_data) in enumerate(images_and_prompts):
            st.subheader(f"Prompt {i+1}: {prompt}")
            st.image(BytesIO(image_data), caption=f"Fetched Drawing {i+1}", use_column_width=True)
    else:
        st.warning("No images found for the most recent round.")
