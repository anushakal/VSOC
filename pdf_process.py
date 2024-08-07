import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from pinecone import ServerlessSpec
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.vectorstores import VectorStoreRetriever
import ast

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
        # Save the uploaded file to a temporary location
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
    
  def answer_query(self, retriever_query = """Frame a MCQ based on the points covered in the document.\n
                    The MCQ should have a question, options and a correct_answer.\n
                    The question, options or the correct answer should not contain any sort of prefix like 'Question:'.\n 
                    The options should not have any sort of numbering or sequencing and seperated by a new line character.\n
                    The correct answer should contain the entire option.\n
                    Print this MCQ as: Question followed 2 new line characters the list of options then 2 new line characters and then correct_answer. No other formatting strictly."""):
      retriever = self.vector_store.as_retriever()
      qa = RetrievalQA.from_chain_type(llm=self.llm, chain_type='stuff', retriever=retriever)
      result = qa.invoke(retriever_query)['result']
      print(type(result))
      print("\nr: ",repr(result))
      parts = result.strip().split("\n\n")
      question = parts[0]
      options = parts[1].split("\n")
      correct_answer = parts[-1].split("\n")[-1]

      return question, options, correct_answer


  def process_pdf(self, uploaded_file):
      pdf_data = self.load_pdf_document(uploaded_file)
      pdf_chunks = self.chunk_pdf_data(pdf_data)
      self.create_embeddings_and_index(pdf_chunks)
      return self.answer_query()


  





  








