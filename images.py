import streamlit as st
import pyodbc
from io import BytesIO

# Azure SQL Server configuration
DB_CONFIG = {
    'server': 'deltahacks2025.database.windows.net',
    'database': 'deltahacks2025',
    'username': 'deltahacks',
    'password': 'password123!',
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


# Function to delete the previous round (removes existing rows)
def delete_previous_round():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("DELETE FROM Drawings")
        
        connection.commit()
        cursor.close()
        connection.close()

        st.success("Previous round replaced successfully!")
    except Exception as e:
        st.error(f"Error deleting previous round: {e}")


# Function to upload new round (new prompts and images)
def upload_images_to_db(prompt1, image_data1, prompt2, image_data2):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Insert new prompts and images for the new round
        cursor.execute("""
            INSERT INTO drawings (prompt, picture) VALUES (?, ?);
            INSERT INTO Drawings (prompt, picture) VALUES (?, ?);
        """, prompt1, image_data1, prompt2, image_data2)

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


# Streamlit Interface
st.title("AI vs Human Drawings")

# Input for the two prompts and file uploaders for the images
prompt1 = st.text_input("Enter the first prompt for your drawing:")
prompt2 = st.text_input("Enter the second prompt for your drawing:")
uploaded_file1 = st.file_uploader("Upload the first drawing image", type=["png", "jpg", "jpeg"])
uploaded_file2 = st.file_uploader("Upload the second drawing image", type=["png", "jpg", "jpeg"])

if st.button("Upload New Round"):
    if prompt1 and prompt2 and uploaded_file1 and uploaded_file2:
        # Delete the previous round first
        delete_previous_round()

        # Convert the images to binary data
        image_data1 = uploaded_file1.read()
        image_data2 = uploaded_file2.read()

        # Upload the new round's images and prompts
        upload_images_to_db(prompt1, image_data1, prompt2, image_data2)
    else:
        st.error("Please provide both prompts and upload both images.")

if st.button("Fetch New Round"):
    # Fetch the images and prompts for the most recent round
    images_and_prompts = fetch_images_from_db()
    if images_and_prompts:
        for i, (prompt, image_data) in enumerate(images_and_prompts):
            st.subheader(f"Prompt {i+1}: {prompt}")
            st.image(BytesIO(image_data), caption=f"Fetched Drawing {i+1}", use_column_width=True)
    else:
        st.warning("No images found for the most recent round.")
