import streamlit as st
from pdf_process import *

openai_api_key = ""

def load_api_keys():
    global openai_api_key
    openai_api_key = st.secrets['OPENAI_API_KEY']

def initialize_session_state():
    if 'pdf_processor' not in st.session_state:
        st.session_state.pdf_processor = None
    if 'file_uploaded' not in st.session_state:
        st.session_state.file_uploaded = False
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = None
    if 'question' not in st.session_state:
        st.session_state.question = None
    if 'options' not in st.session_state:
        st.session_state.options = []
    if 'correct_answer' not in st.session_state:
        st.session_state.correct_answer = None
    if 'answer_feedback' not in st.session_state:
        st.session_state.answer_feedback = None 
    if 'question_difficulty' not in st.session_state:
        st.session_state.question_difficulty = "easy"  # Start with easy difficulty
    if 'difficulty_level' not in st.session_state:
        st.session_state.difficulty_levels =["easy", "medium", "hard"]  

def reset_session_state():
    st.session_state.pdf_processor = None
    st.session_state.file_uploaded = False
    st.session_state.quiz_started = None
    reset_question_state()
   
def reset_question_state():
    st.session_state.question = None
    st.session_state.options = []
    st.session_state.correct_answer = None


def display_title():
    st.title("Vizuara Adaptive Q/A Generator")

def update_difficulty_level():
    difficulty_levels = st.session_state.difficulty_levels
    current_index = difficulty_levels.index(st.session_state.question_difficulty)
    print(f"diff earlier:{st.session_state.question_difficulty}")
    if st.session_state.answer_feedback:
        # Move up the difficulty level if possible
        if current_index < len(difficulty_levels) - 1:
            st.session_state.question_difficulty = difficulty_levels[current_index + 1]
    else:
        # Move down the difficulty level if possible
        if current_index > 0:
            st.session_state.question_difficulty = difficulty_levels[current_index - 1]
    print(f"diff later:{st.session_state.question_difficulty}")


def get_question_from_pdf():
    if st.session_state.pdf_processor:
        question, options, correct_answer = st.session_state.pdf_processor.answer_query(st.session_state.question_difficulty)
        st.session_state.question = question
        st.session_state.options = options
        st.session_state.correct_answer = correct_answer
        st.session_state.answer_feedback = None

def display_question():
    # Display the current difficulty level
    st.markdown(f"**Current Difficulty Level: {st.session_state.question_difficulty.capitalize()}**")
    # Display the question
    st.markdown(f"**{st.session_state.question}**")
    form = st.form(key="quiz")
    user_choice = form.radio("Choose an answer:", st.session_state.options, index=None)
    submitted = form.form_submit_button("Submit your answer")
    if submitted:
        if user_choice == st.session_state.correct_answer:
            st.success("Correct! Well done")
            st.session_state.answer_feedback = True
        else:
            st.error("Incorrect!")
            st.markdown(f"You selected: {user_choice}\n  Correct Answer: **{st.session_state.correct_answer}**")
            st.session_state.answer_feedback = False
        update_difficulty_level()
        reset_question_state()
        
def main():
    load_api_keys()
    initialize_session_state()
    display_title()
    if not st.session_state.file_uploaded:
        uploaded_file = st.file_uploader("Upload a PDF file for generating questions", type="pdf")
        if uploaded_file:
            st.session_state.file_uploaded = True
            st.write(f"Uploaded File name: {uploaded_file.name}")
            with st.spinner("Processing the PDF"):
                st.session_state.pdf_processor = Pdf(openai_api_key)
                st.session_state.pdf_processor.process_pdf(uploaded_file)
    
    if st.session_state.file_uploaded:
        col1, col2 = st.columns(2)
        with col1:
            if st.button('Start Quiz', key='start'):
                st.session_state.quiz_started = True
        
        with col2:
            if st.button('Stop Quiz', key='stop'):
                st.session_state.quiz_started = False
    
    if st.session_state.quiz_started == True:
        if st.session_state.question == None:
            get_question_from_pdf()

        display_question()
        
        if st.session_state.answer_feedback is not None:
            if st.button("Next"):
                with st.spinner("Preparing next question"):
                    pass
                #reset_question_state()
                # get_question_from_pdf()
    
    elif st.session_state.quiz_started == False:
        st.subheader("Quiz stopped!")
        reset_session_state()


if __name__ == "__main__":
    main()