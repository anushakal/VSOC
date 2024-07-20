import streamlit as st
from dotenv import find_dotenv, load_dotenv
from pdf_process import *

def load_api_keys():
    load_dotenv(find_dotenv(".env.txt"))

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

def process_pdf(pdf_processor, uploaded_file):
    st.session_state.file_uploaded = True
    st.write("Processing the PDF...")
    pdf_process = pdf_processor.process_pdf(uploaded_file)
    if pdf_process == True:
        st.session_state.pdf_processed = True
        st.write("PDF processed successfully! You can now generate questions.")
    else:
        st.error("Failed to process the PDF.")

def generate_quiz(pdf_processor):
    if st.session_state.pdf_processed and st.button("Generate Quiz"):
        st.write("Generating quiz based on the processed PDF...")
        answer = pdf_processor.generate_questions()
        st.write(answer)

def main():

    load_api_keys()
    pdf_processor = Pdf()
    initialize_session_state()
    st.title("Vizuara Adaptive Q/A Generator")
    st.subheader("Answer adaptive questions based on your uploaded PDF!")
    uploaded_file = upload_pdf()
    if st.button("Generate Quiz"):
        if uploaded_file:
            st.write("generating quiz")
            answer = pdf_processor.process_pdf(uploaded_file)
            st.write(answer)
        else:
            st.error("Please upload a PDF file before processing.")



if __name__ == "__main__":
    main()