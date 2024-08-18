import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
import re
import json

class Pdf():

  vector_store = None
  openai_api_key = None
  llm = None
  memory = None

  def __init__(self, openai_api_key) -> None:
      self.openai_api_key = openai_api_key
      self.vector_store = None
      self.llm = ChatOpenAI(temperature=1, model_name="gpt-3.5-turbo")
      self.memory = ConversationBufferMemory()

  def load_pdf_document(self, uploaded_file):
    if uploaded_file.type == "application/pdf":
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())
    
        loader = PyPDFLoader(uploaded_file.name)
        data = loader.load()
        os.remove(uploaded_file.name)
        return data
    
  def chunk_pdf_data(self, pdf_data):
      text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1024, chunk_overlap = 0)
      chunks = text_splitter.split_documents(pdf_data)
      return chunks

  def create_embeddings_and_index(self, pdf_chunks):
      embeddings = OpenAIEmbeddings(model = 'text-embedding-3-small', dimensions=1536, api_key = self.openai_api_key)
      self.vector_store = FAISS.from_documents(pdf_chunks, embeddings)
    


  def answer_query(self, difficulty):
        # Limit to the last N questions
        #N = 10
        #recent_questions = self.memory.chat_memory[-N:]
        #previous_questions = "\n".join([f"Q: {q['question']} (Difficulty: {q['difficulty']})" for q in recent_questions])
        
        # Construct the retriever query with memory
        #retriever_query = f"""
        #Previous questions and their difficulty levels:
        #{previous_questions}
        print(type(self.memory.chat_memory))
    
        retriever_query = f"""
        Please carefully analyze the document and generate a unique and novel multiple-choice question (MCQ) that tests understanding of different aspects of the content. 
        Ensure that the question is different from any previous questions and is designed with the following difficulty level in mind: {difficulty}. 
        Consider what makes a question easier or harder (e.g., more abstract concepts, more similar answer choices for harder questions).
        Refer to your memory so that questions are not repeated

        The question must be strictly in MCQ format, without any fill-in-the-blank, explanation, or true/false questions.

        The output should be in JSON format with the following structure:
        {{
            "question": "Text of the question",
            "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
            "correct_answer": "Correct Answer"
        }}

        Ensure that the JSON contains only the keys "question", "options", and "correct_answer", with no extra fields.
        """

        
        retriever = self.vector_store.as_retriever()
        qa = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type='stuff',
            retriever=retriever,
            memory=self.memory
        )
        result = qa.invoke({"query": retriever_query})

        # Print the raw JSON output for inspection
        print("Raw JSON LLM Output:\n", repr(result['result']))

        # Clean up and parse the output
        clean_result = re.sub(r'^```json\s*|\s*```$', '', result['result'].strip())

        try:
            data = json.loads(clean_result)
            question = data['question']
            options = data['options']
            correct_answer = data['correct_answer']
        except json.JSONDecodeError:
            raise ValueError(f"Unexpected format in the generated question. The output was not valid JSON.\nCleaned Output: {repr(clean_result)}")
        
        # # Add the new question to memory
        # self.memory.add_memory({
        #     "question": question,
        #     "difficulty": difficulty
        # })

        return question, options, correct_answer

  def process_pdf(self, uploaded_file):
      pdf_data = self.load_pdf_document(uploaded_file)
      pdf_chunks = self.chunk_pdf_data(pdf_data)
      self.create_embeddings_and_index(pdf_chunks)


