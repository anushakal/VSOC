import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.vectorstores import VectorStoreRetriever
import re
import json

class Pdf():

  vector_store = None
  openai_api_key = None
  llm = None

  def __init__(self, openai_api_key) -> None:
      self.openai_api_key = openai_api_key
      self.vector_store = None
      self.llm = ChatOpenAI(temperature=1, model_name="gpt-3.5-turbo")

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
    
  # def answer_query(self, difficulty, 
  #                retriever_query="""
  #                Please analyze the document and frame a unique Multiple choice question that focuses on different aspects of the content.
  #                The question should be of MCQ format strictly. No fill in the blanks or explanation or true or false questions.
  #                The MCQ should have a question, options, and a correct_answer.
  #                The MCQ should be unique and not be repetitive in nature.
  #                There should strictly be no prefixes like 'Question:' or 'Correct Answer:' or 'Option'.
  #                The options should not have any sort of numbering or sequencing like 1. or a. or A. or '-' or (A) or (a) or a).
  #                The correct answer should contain the entire option.
  #                The formatting should be:
  #                Text of the question, ending with 2 new line characters
  #                Option 1, ending with one single new line character
  #                Option 2, ending with one single new line character
  #                Option 3, ending with one single new line character
  #                Option 4, ending with 2 new line characters
  #                Correct Answer, ending with one single new line character
  #                No other formatting or extra lines should be present.
  #                """):
    
  #   retriever_query += f"\nAdjust the difficulty of the question to be {difficulty}."
  #   retriever = self.vector_store.as_retriever()
  #   qa = RetrievalQA.from_chain_type(llm=self.llm, chain_type='stuff', retriever=retriever)
  #   result = qa.invoke(retriever_query)['result']
    
  #   # Print the cleaned output for inspection
  #   print("Cleaned LLM Output:\n", repr(result))
    
  #   # Attempt to split the result as expected
  #   parts = result.strip().split("\n\n")

  #   # Check if splitting is working correctly
  #   if len(parts) < 3:
  #       raise ValueError(f"Unexpected format in the generated question. Please check the retriever_query template.\nRaw Output: {repr(result)}")
    
  #   question = parts[0].strip()

  #   options = parts[1].strip().split("\n")
  #   options = [re.sub(r'^\d+\.\s*|^[a-zA-Z]\.\s*|^-', '', option).strip() for option in options]
    
  #   correct_answer = parts[-1].strip()
  #   correct_answer = re.sub(r'^\d+\.\s*|^[a-zA-Z]\.\s*|^-', '', correct_answer).strip()
  #   correct_answer = re.sub(r'^Correct Answer:\s*', '', correct_answer).strip()

  #   return question, options, correct_answer


  def answer_query(self, difficulty, 
                 retriever_query="""
                 Please analyze the document and frame a unique Multiple choice question that focuses on different aspects of the content.
                 The question should be of MCQ format strictly. No fill in the blanks or explanation or true or false questions.
                 The output should be in JSON format with the following structure:
                 {
                     "question": "Text of the question",
                     "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                     "correct_answer": "Correct Answer"
                 }
                 The JSON should contain no extra fields, just the keys "question", "options", and "correct_answer".
                 """):
    
    retriever_query += f"\nAdjust the difficulty of the question to be {difficulty}."
    retriever = self.vector_store.as_retriever()
    qa = RetrievalQA.from_chain_type(llm=self.llm, chain_type='stuff', retriever=retriever)
    result = qa.invoke(retriever_query)['result']

    # Print the raw JSON output for inspection
    print("Raw JSON LLM Output:\n", repr(result))
    print(difficulty)

    # Remove Markdown code block formatting if present
    clean_result = re.sub(r'^```json\s*|\s*```$', '', result.strip())

    # Parse the cleaned JSON output
    try:
        data = json.loads(clean_result)
        question = data['question']
        options = data['options']
        correct_answer = data['correct_answer']
    except json.JSONDecodeError:
        raise ValueError(f"Unexpected format in the generated question. The output was not valid JSON.\nCleaned Output: {repr(clean_result)}")
    
    return question, options, correct_answer



  def process_pdf(self, uploaded_file):
      pdf_data = self.load_pdf_document(uploaded_file)
      pdf_chunks = self.chunk_pdf_data(pdf_data)
      self.create_embeddings_and_index(pdf_chunks)


