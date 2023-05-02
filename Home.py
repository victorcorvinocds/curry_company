import streamlit as st
from PIL import Image

st.set_page_config(page_title="Home")
image= Image.open('logo.jpg')
st.sidebar.image(image, width=120)
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fasted Delivery in Town')
st.sidebar.markdown("""---""")
st.write("# Curry Company Growth Dashboard")