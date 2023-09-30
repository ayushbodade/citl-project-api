import streamlit as st
import requests

st.header('GPT Banker', divider='rainbow')
st.header('_Ask questions about_ :blue[Annual Reports] :sunglasses:')

import streamlit as st
import requests

# Streamlit UI
st.title("PDF Uploader")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file:
    st.write("File uploaded successfully!")

    # Display file details
    file_details = {"Filename": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": uploaded_file.size}
    st.write(file_details)

    # Button to upload the file
    if st.button("Upload"):
        # POST request to Flask server
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
        response = requests.post("http://127.0.0.1:5000/upload", files=files)

        # Display server response
        st.write(response.json())
