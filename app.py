import streamlit as st
from streamlit_drawable_canvas import st_canvas
from prompts import prompts
import random
import requests
from PIL import Image
from io import BytesIO
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
    else:
        upload_image_to_db(st.session_state.prompt, None)
    
        

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

        st.title("Prompt: " + st.session_state.prompt)
        
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