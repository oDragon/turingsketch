import streamlit as st
from streamlit_drawable_canvas import st_canvas
from prompts import prompts
import random
import requests
from PIL import Image
from io import BytesIO
import time
from streamlit.components.v1 import html
import asyncio
import aiohttp
from images import is_first_player, upload_image_to_db, delete_previous_round

def play():
    # Update the screen state to "play"
    st.session_state.screen = "play"
    st.session_state.prompt = random.choice(prompts)
    if is_first_player() == True:
        delete_previous_round()
        upload_image_to_db(st.session_state.prompt, None)
        if "start_time" not in st.session_state:
            st.write("searching for players...")
            while True:
                time.sleep(1)
                if is_first_player() == True:
                    st.session_state.start_timer = True
                    break
    else:
        upload_image_to_db(st.session_state.prompt, None)
        st.session_state.start_timer = True

def done():
    st.session_state.screen = "guess"

def main():
    # Initialize the screen in session state
    if "screen" not in st.session_state:
        st.session_state.screen = "home"
    
    if st.session_state.screen == "home":
        st.button(label="Play", on_click=play)

    elif st.session_state.screen == "play":
        # print(prompt)

        st.header("Prompt: " + st.session_state.prompt)
        
        # Create three columns
        col1, col2, col3 = st.columns(3)

        # Add widgets to each column
        with col1:
            stroke_width = st.slider("Stroke width", 1, 25, 3)

        with col2:
            stroke_color = st.color_picker("Stroke color", "#000000")

        with col3:
            bg_color = st.color_picker("Background color", "#FFFFFF")

        # Create the canvas
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            background_color=bg_color,
            height=512,
            width=512,
            drawing_mode="freedraw",
            key="canvas",
        )

        my_html = """
        <style>
            body {
                margin: 0;
                padding: 0;
                height: 50%;
            }
            #timer-container {
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100%;
                width: 100%;
                margin: 0;  /* Remove extra space at the top */
                padding: 0; /* Remove padding if any */
            }
        </style>
        <script>
        function startTimer(duration, display) {
            var timer = duration, minutes, seconds;
            setInterval(function () {
                minutes = parseInt(timer / 60, 10)
                seconds = parseInt(timer % 60, 10);

                minutes = minutes < 10 ? "0" + minutes : minutes;
                seconds = seconds < 10 ? "0" + seconds : seconds;

                display.textContent = minutes + ":" + seconds;

                if (--timer < 0) {
                    timer = duration;
                }
            }, 1000);
        }

        window.onload = function () {
            var timeLimit = 30,
                display = document.querySelector('#time');
            startTimer(timeLimit, display);
        };
        </script>

        <body>
        <div>Time left: <span id="time">00:30</span></div>
        </body>
        """

        if "start_timer" in st.session_state:
            html(my_html)

        st.button(label="Done", on_click=done)

        url = f"https://pollinations.ai/p/A very poorly drawn black and white image of a {st.session_state.prompt}, created in under 30 seconds with minimal detail. The drawing should use rough, uneven lines, simple shapes, and only basic colors. It should look like it was drawn hurriedly in a basic MSpaint, with no shading or intricate features. The background is plain white.?width=512&height=512"
        st.session_state.img = requests.get(url)        

        
    elif st.session_state.screen == "guess":
        st.title("which is AI?")

        image_bytes = BytesIO(st.session_state.img.content)

        # Optionally, open the image using PIL (not strictly necessary)
        image = Image.open(image_bytes)

        # Display the image in Streamlit
        st.image(image)
        
main()