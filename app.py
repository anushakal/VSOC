import streamlit as st
from pdf_process import *

pinecone_api_key = ""
openai_api_key = ""

def load_api_keys():
    global pinecone_api_key
    pinecone_api_key = st.secrets['PINECONE_API_KEY']
    global openai_api_key
    openai_api_key = st.secrets['OPENAI_API_KEY']

def initialize_session_state():
    if 'file_uploaded' not in st.session_state:
        st.session_state.file_uploaded = False
    if 'pdf_processed' not in st.session_state:
        st.session_state.pdf_processed = False

def upload_pdf():
    if not st.session_state.file_uploaded:
        uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
        return uploaded_file
    return None


def main():

    load_api_keys()
    pdf_processor = Pdf(pinecone_api_key, openai_api_key)
    initialize_session_state()
    st.title("Vizuara Adaptive Q/A Generator")
    st.subheader("Answer adaptive questions based on your uploaded PDF!")
    uploaded_file = upload_pdf()
    if st.button("Generate Quiz"):
        if uploaded_file:
            st.write(f"File name: {uploaded_file.name}")
            st.write(f"File type: {uploaded_file.type}")
            st.write(f"File size: {uploaded_file.size} bytes")
            st.write("PDF DATA:")
            answer = pdf_processor.process_pdf(uploaded_file)
            st.write(answer)
        else:
            st.error("Please upload a PDF file before processing.")



if __name__ == "__main__":
    main()