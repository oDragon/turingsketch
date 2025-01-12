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

# Initial Page Configurations
icon = Image.open('assets/logo-small.png')
st.set_page_config(
        page_title="TuringSketch",
        page_icon=icon
    )


def play():
    """
    Transition to the play screen.
    """
    # Update the screen state to "play"
    st.session_state.screen = "play"
    st.session_state.prompt = random.choice(prompts)

    # If the player is the first player, delete the previous round and upload the new prompt
    if is_first_player() == True:
        delete_previous_round()
        upload_image_to_db(st.session_state.prompt, None)
        if "start_time" not in st.session_state:
            
            # Loading gif
            col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns(9)
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
                    #st.session_state.start_timer = True
                    break

    # If the player is the second player, fetch the images from the database
    else:
        images = fetch_images_from_db()
        otherPrompt = images[0].prompt
        while otherPrompt == st.session_state.prompt:
            st.session_state.prompt = random.choice(prompts)
        upload_image_to_db(st.session_state.prompt, None)


def main():
    ###################################################
    #                     HEADER                      #
    ###################################################
    logo = Image.open("assets/logo.png")
    st.image(logo)


    ###################################################
    #                   HOME SCREEN                   #
    ###################################################
    # Initialize the screen in session state
    if "screen" not in st.session_state:
        st.session_state.screen = "home"

    # Rules and Play button
    if st.session_state.screen == "home":
        st.markdown("<p style='text-align: center;'>Welcome to TuringSketch! The game where you have to guess which drawing was made by AI.</p>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: red;'>Rules</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>You will be placed into a match against another player.</p>"
                "<p style='text-align: center;'>You will be given a prompt to draw.</p>"
                "<p style='text-align: center;'>After drawing, you will be shown two images: one drawn by AI and one drawn by a human.</p>"
                "<p style='text-align: center;'>Your task is to guess which image was drawn by AI.</p>", unsafe_allow_html=True)

        # Create seven columns
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
        with col1:
            pass
        with col2:
            pass
        with col3:
            pass
        with col4:
            st.button(label="Play", on_click=play)
        with col5:
            pass
        with col6:
            pass
        with col7:
            pass


    ###################################################
    #                   PLAY SCREEN                   #
    ###################################################
    elif st.session_state.screen == "play":
        st.header(f"Draw a {st.session_state.prompt}!")
        
        # Drawing Tools
        col1, col2, col3 = st.columns(3)
        with col1:
            stroke_width = st.slider("Stroke width", 1, 25, 3)
        with col2:
            stroke_color = st.color_picker("Stroke color", "#000000")
        with col3:
            bg_color = st.color_picker("Background color", "#FFFFFF")

        # Drawing Canvas
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

        def to_blob(img:np.ndarray) -> bytes | None:
            """
            Converts the dataclass instance to a BLOB.
            """
            image_data_blob = img.tobytes() if img is not None else None
            return image_data_blob

        def guess() -> None:
            """
            Transition to the guess screen and upload the image to the database.
            """
            st.session_state.screen = "guess"
            blob = to_blob(canvas_result.image_data)
            upload_image_to_db(st.session_state.prompt, blob)
            
        st.button(label="Done", on_click=guess)

        url = f"https://pollinations.ai/p/A poorly drawn black and white line art of a {st.session_state.prompt}, created in under 30 seconds by a 3 year old child. The drawing should use lines that are solid, wiggly, and hex code #000000. It should look like it was drawn in MSpaint, with no shading and no details. Only use simple shapes. The background color should be #FFFFFF. All lines should have the same width.?width=512&height=512"
        st.session_state.img = requests.get(url)
        

    ###################################################
    #                  GUESS SCREEN                   #
    ###################################################
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


    ###################################################
    #                 FINISH SCREEN                   #
    ###################################################
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