import streamlit as st
from streamlit_drawable_canvas import st_canvas, CanvasResult
from prompts import prompts
import random
import requests
from PIL import Image
from io import BytesIO
import time
import numpy as np
import base64
from model import is_first_player, upload_image_to_db, delete_previous_round, fetch_images_from_db

# Page icon
icon = Image.open('assets/logo-small.png')

st.set_page_config(
        page_title="TuringSketch",
        page_icon=icon
    )

page_bg_img = """
    <style>
    background-color: #f7f7f7;
    </style>
    """
st.markdown(page_bg_img, unsafe_allow_html=True)
# Set page title
def play():
    # Update the screen state to "play"
    st.session_state.screen = "play"
    st.session_state.prompt = random.choice(prompts)
    if is_first_player() == True:
        delete_previous_round()
        upload_image_to_db(st.session_state.prompt, None)
        if "start_time" not in st.session_state:
            
            # Loading gif
            # Create nine columns
            col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns(9)
            # Add widgets to each column
            with col1:
                pass
            with col2:
                pass
            with col3:
                pass
            with col4:
                pass
            with col5:
                file_ = open("assets/loading.gif", "rb")
                contents = file_.read()
                data_url = base64.b64encode(contents).decode("utf-8")
                file_.close()

                st.markdown(
                    f'<img src="data:image/gif;base64,{data_url}" alt="loading circle" style="width: 50px;">',
                    unsafe_allow_html=True,
                )
            with col6:
                pass
            with col7:
                pass
            with col8:
                pass
            with col9:
                pass

            st.markdown("<p style='text-align: center;'>Searching for players...</p>", unsafe_allow_html=True)
            st.divider()
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
        st.markdown("<p style='text-align: center;'>Welcome to TuringSketch! The game where you have to guess which drawing was made by AI.</p>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: red;'>Rules</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>You will be placed into a match against another player.</p>"
                "<p style='text-align: center;'>You will be given a prompt to draw.</p>"
                "<p style='text-align: center;'>After drawing, you will be shown two images: one drawn by AI and one drawn by a human.</p>"
                "<p style='text-align: center;'>Your task is to guess which image was drawn by AI.</p>", unsafe_allow_html=True)
        

        # Create seven columns
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
        # Add widgets to each column
        with col1:
            pass
        with col2:
            pass
        with col3:
            pass
        with col4:
            if 'button_clicked' not in st.session_state:
                st.session_state.button_clicked = False

                st.button(label="Play", on_click=play, disabled=st.session_state.button_clicked)
                st.session_state.button_clicked = True
            else:
                st.write('Button is disabled.')
        with col5:
            pass
        with col6:
            pass
        with col7:
            pass

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
        st.title("Which picture is made by AI?")
        
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
            st.session_state['answer'] = answer
            st.session_state['ground_truth'] = ground_truth

    elif st.session_state.screen == "finish":
        ground_truth = st.session_state['ground_truth']
        answer = st.session_state['answer']

        if answer == ground_truth:
            st.markdown("<p style='text-align: center;'>Correct!</p>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='text-align: center;'>Incorrect!</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'>The AI drawing is on the {ground_truth}.</p>", unsafe_allow_html=True)

        # Create seven columns
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
        # Add widgets to each column
        with col1:
            pass
        with col2:
            pass
        with col3:
            pass
        with col4:
            st.button(label="Play Again", on_click=play)
        with col5:
            pass
        with col6:
            pass
        with col7:
            pass

main()