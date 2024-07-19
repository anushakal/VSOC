import streamlit as st
from dotenv import find_dotenv, load_dotenv
import pdf_process as pp

def load_api_keys():
    #load_dotenv(".\VSOC\.env.txt")
    load_dotenv(find_dotenv(".env.txt"))

def main():

    load_api_keys()

    st.title("Vizuara Adaptive Q/A Generator")
    st.subheader("Upload a PDF file to get started")

    # File uploader for PDF and DOC files
    uploaded_file = st.file_uploader("", type=["pdf"])
    
    if uploaded_file is not None:
        st.success("File uploaded successfully!")
        pp.process_pdf(uploaded_file)

        query = st.text_input("Enter your query:")
        if st.button("Submit Query"):
            answer = pp.answer_query(query)
            st.text_area("Result:", answer)



if __name__ == "__main__":
    main()