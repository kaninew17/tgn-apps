import streamlit as st


st.title('my first streamlit app')

name = st.text_input('enter your name')

if st.button('say hello'):
    if name:
        st.success(f'hello{name},welcome to my page')
    else:
        st.warning('enter your name')