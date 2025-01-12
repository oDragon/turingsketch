import streamlit as st
from streamlit_drawable_canvas import st_canvas, CanvasResult
from prompts import prompts
import random
import requests
from PIL import Image
from io import BytesIO
import time
from streamlit.components.v1 import html
import numpy as np
import base64
import asyncio
import aiohttp
from model import is_first_player, upload_image_to_db, delete_previous_round, fetch_images_from_db

# Page icon
#icon = Image.open('img/streamlit-mark-light.png')

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
        images = fetch_images_from_db()
        otherPrompt = images[0].prompt
        print(otherPrompt)
        while otherPrompt == st.session_state.prompt:
            st.session_state.prompt = random.choice(prompts)
        upload_image_to_db(st.session_state.prompt, None)
        st.session_state.start_timer = True
    
def main():
    logo = Image.open("assets/logo.png")
    st.image(logo)
    # Initialize the screen in session state
    if "screen" not in st.session_state:
        st.session_state.screen = "home"

    if st.session_state.screen == "home":
        st.button(label="Play", on_click=play)

    elif st.session_state.screen == "play":

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
            var interval = setInterval(function () {
                minutes = parseInt(timer / 60, 10)
                seconds = parseInt(timer % 60, 10);

                minutes = minutes < 10 ? "0" + minutes : minutes;
                seconds = seconds < 10 ? "0" + seconds : seconds;

                display.textContent = minutes + ":" + seconds;

                if (--timer < 0) {
                    clearInterval(interval);
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
        </form>
        </body>
        """

        if "start_timer" in st.session_state:
            html(my_html)

        def to_blob(img):
            """Converts the dataclass instance to a BLOB."""
            image_data_blob = img.tobytes() if img is not None else None
            return image_data_blob

        def done():
            st.session_state.screen = "guess"
            blob = to_blob(canvas_result.image_data)
            
            upload_image_to_db(st.session_state.prompt, blob)
            
        st.button(label="Done", on_click=done)

        url = f"https://pollinations.ai/p/A very poorly drawn black and white image of a {st.session_state.prompt}, created in under 30 seconds with minimal detail. The drawing should use rough, uneven lines, simple shapes, and only basic colors. It should look like it was drawn hurriedly in a basic MSpaint, with no shading or intricate features. The background is plain white.?width=512&height=512"
        st.session_state.img = requests.get(url)
        
    elif st.session_state.screen == "guess":
        st.title("which is AI?")
        
        

        def from_blob(image_data_blob):
            """Reconstructs the dataclass from a BLOB."""
            image_data = np.frombuffer(image_data_blob, dtype=np.uint8).reshape(512, 512, 4) if image_data_blob else None
            return CanvasResult(image_data=image_data)

        while "otherDrawing" not in st.session_state or "otherImg" not in st.session_state:
            images = fetch_images_from_db()
            for i, (prompt, image_data) in enumerate(images):
                if prompt != st.session_state.prompt and "otherImg" not in st.session_state:
                    url = f"https://pollinations.ai/p/A very poorly drawn black and white image of a {prompt}, created in under 30 seconds with minimal detail. The drawing should use rough, uneven lines, simple shapes, and only basic colors. It should look like it was drawn hurriedly in a basic MSpaint, with no shading or intricate features. The background is plain white.?width=512&height=512"
                    # st.image(Image.open(BytesIO((requests.get(url)).content)))
                    st.session_state.otherImg = requests.get(url)
                if prompt != st.session_state.prompt and image_data is not None and "otherDrawing" not in st.session_state:
                    unblob = from_blob(image_data)
                    # st.image(unblob.image_data)
                    st.session_state.otherDrawing = unblob.image_data
            time.sleep(1)

        ai_image = Image.open(BytesIO((st.session_state.otherImg).content))
        human_image = st.session_state.otherDrawing

        # Put the images in two columns, randomized order
        col1, col2 = st.columns(2)
        rand = random.choice([0,1])
        ground_truth = 'left' if rand == 0 else 'right'
        with col1:
            if rand == 0:
                st.image(ai_image)
            else:
                st.image(human_image)
            st.button(label="This is AI.", on_click=lambda: finish("left", ground_truth), key="left")
        with col2:
            if rand == 1:
                st.image(ai_image)
            else:
                st.image(human_image)
            st.button(label="This is AI.", on_click=lambda: finish("right", ground_truth), key="right")


        def finish(answer, ground_truth):
            """
            Set the screen state to "finish" when the user clicks the button.
            Show the answers.
            """
            st.session_state.screen = "finish"
            if answer == ground_truth:
                st.write("Correct!")
            else:
                st.write("Incorrect!")
            st.write(f"The AI drawing is on the {ground_truth}.")

main()