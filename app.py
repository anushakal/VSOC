import streamlit as st
from pdf_process import *

openai_api_key = ""

def load_api_keys():
    global openai_api_key
    openai_api_key = st.secrets['OPENAI_API_KEY']

def initialize_session_state():
    if 'file_uploaded' not in st.session_state:
        st.session_state.file_uploaded = False
    if 'selected_option' not in st.session_state:
        st.session_state.selected_option = None
    if 'question' not in st.session_state:
        st.session_state.question = None
    if 'options' not in st.session_state:
        st.session_state.options = []
    if 'correct_answer' not in st.session_state:
        st.session_state.correct_answer = None

def upload_pdf():
    if not st.session_state.file_uploaded:
        uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
        return uploaded_file
    return None

def display_title():
    st.title("Vizuara Adaptive Q/A Generator")
    st.subheader("Answer adaptive questions based on your uploaded PDF!")

def get_question_from_pdf(pdf_processor):
    question, options, correct_answer = pdf_processor.answer_query()
    st.session_state.question = question
    st.session_state.options = options
    st.session_state.correct_answer = correct_answer
    st.session_state.selected_option = None

def display_question():
    if st.session_state.question:
        st.write("Following is the quiz based on the uploaded PDF:")
        st.markdown(f"**{st.session_state.question}**")

        # Display the options as radio buttons
        st.session_state.selected_option = st.radio("Select an option:", st.session_state.options)
        
        # Display the selected answer when the button is clicked
        if st.button("Display answer"):
            if st.session_state.selected_option:
                st.write(f"You selected: {st.session_state.selected_option}")
                st.markdown(f"**Correct Answer: {st.session_state.correct_answer}**")
            else:
                st.write("You have not selected any option yet.")

def main():

    load_api_keys()
    pdf_processor = Pdf(openai_api_key)
    initialize_session_state()
    display_title()
    uploaded_file = upload_pdf()
    if st.button("Generate Quiz"):
        if uploaded_file:
            #st.session_state.file_uploaded = True
            st.write(f"Uploaded File name: {uploaded_file.name}")
            pdf_processor.process_pdf(uploaded_file)
            get_question_from_pdf(pdf_processor)
        else:
            st.error("Please upload a PDF file before processing.")
    
    display_question()

    
    



if __name__ == "__main__":
    main()