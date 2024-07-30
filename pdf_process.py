import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from pinecone import ServerlessSpec
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.vectorstores import VectorStoreRetriever

class Pdf():

  vector_store = None
  openai_api_key = None

  def __init__(self, openai_api_key) -> None:
      self.openai_api_key = openai_api_key
      self.vector_store = None

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
    
  def answer_query(self, retriever_query = "Frame 5 MCQs based on the points covered in the document."):
      retriever = self.vector_store.as_retriever()
      llm = ChatOpenAI(temperature=1, model_name="gpt-3.5-turbo")
      qa = RetrievalQA.from_chain_type(llm=llm, chain_type='stuff', retriever=retriever)
      results = qa.invoke(retriever_query)
      print(results)
      return results['result']

  def process_pdf(self, uploaded_file):
      pdf_data = self.load_pdf_document(uploaded_file)
      pdf_chunks = self.chunk_pdf_data(pdf_data)
      self.create_embeddings_and_index(pdf_chunks)
      answer = self.answer_query()
      return answer


  





  








