import streamlit as st
from discord import retrieveImage

st.image(retrieveImage()[0]["embeds"][0]["image"]["url"])

