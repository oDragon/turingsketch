# [NAME]

In [NAME], players face off in a Turing Test-inspired game with a creative twist, reminiscent of [skribbl.io](https://skribbl.io/)!

Each player receives a different prompt to draw something within 30 seconds. Meanwhile, an AI creates its own drawings based on the same prompts. When the timer runs out, players are shown the drawing their opponent made along with the AI's corresponding drawing. The challenge? Guess which image was created by the AI and which one was drawn by a human!

This project was submitted to DeltaHacks XI!

## How to run

1. Clone the repository:
    ```bash
    git clone https://github.com/oDragon/deltahacks11
    ```
2. Navigate to the project directory:
    ```bash
    cd deltahacks11
    ```
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. In [Microsoft Azure](https://portal.azure.com), create a server and database:
    ```sql
    CREATE TABLE drawings(
        prompt VARCHAR(MAX) NOT NULL,
        picture VARBINARY(MAX)
    )

    INSERT INTO drawings(prompt)
    VALUES (cat), (car)
    ```

5. Create a `.env` file in the project directory with the following content:
    ```plaintext
    DB_SERVER = <your_db_server>
    DB_NAME = <your_db_name>
    DB_USERNAME = <your_db_username>
    DB_PASSWORD = <your_db_password>
    ```

6. You may need to install version 17 of Microsoft ODBC Driver from [Microsoft](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16#version-17).

7. In command prompt, run the Streamlit application:
    ```bash
    streamlit run app.py
    ```


6. Open your web browser and go to `http://localhost:8501` to access the application.

## How we built it
We used Streamlit and Python for the app's front-end and back-end development.  For the database, we used Azure SQL Server to store users' images during games so that we wouldn't need to use Web Sockets.

## Challenges we ran into
We spent a long time searching for a free image generation API that could produce "low-quality MS Paint style" images.  At the same time, we were fine-tuning prompts to match this style across every API we tried.  Combining these two tasks led to double the time spent, and double the frustration!

[TIMER]

## Accomplishments that we're proud of
We're proud of successfully integrating image generation into our game, adding a unique twist to the traditional Turing Test.  Despite challenges in finding the right tools and APIs, we managed to overcome them and efficiently incorporate image generation and database management into the project.

## What We Learned
Throughout this process, we gained valuable hands-on experience working with APIs and image generation models.  We also learned how to combine back end and front end logic using streamlit, python, and Azure SQL Server.

## What's next for [NAME]
Currently, [NAME] supports only two players at a time.  Our next steps include expanding to support multiple game sessions, custom rooms, and a friends system for a more dynamic experience.

## Technologies Used
Python, Streamlit, Azure MSSQL, pollinations.ai