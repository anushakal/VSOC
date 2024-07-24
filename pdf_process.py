import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pinecone
from langchain_community.vectorstores import Pinecone
from langchain_openai import OpenAIEmbeddings
from pinecone import PodSpec
from pinecone import ServerlessSpec
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
      
class Pdf():

  pc = None
  vector_store = None
  pinecone_api_key = None
  openai_api_key = None

  def __init__(self, pinecone_api_key, openai_api_key) -> None:
      self.pinecone_api_key = pinecone_api_key
      self.openai_api_key = openai_api_key
      self.vector_store = None
      self.pc = pinecone.Pinecone(api_key = self.pinecone_api_key)

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

  def delete_pinecone_index(self, index_name='all'):
    if index_name == 'all':
      indexes = self.pc.list_indexes().names()
      print("Deleting all indices")
      for index in indexes:
        self.pc.delete_index(index)

    else:
      self.pc.delete_index(index_name)

  def insert_or_fetch_embeddings(self, index_name, chunks):
      embeddings = OpenAIEmbeddings(model = 'text-embedding-3-small', dimensions=1536, api_key = self.openai_api_key)

      if index_name in self.pc.list_indexes().names():
        print(f'Index name: {index_name} already exists, loading embeddings')
        self.vector_store = Pinecone.from_existing_index(index_name,embeddings)
        print("fetched index")
      else:
        print(f"Creating Index: {index_name} and embeddings")
        #pc.create_index(name=index_name, dimension=1536, metric='cosine', spec = PodSpec(environment='gcp-starter'))
        self.pc.create_index(
          name = index_name,
          dimension = 1536,
          metric = 'cosine',
          spec = ServerlessSpec(
              cloud = 'aws',
              region = 'us-east-1'
          )
        )
        self.vector_store = Pinecone.from_documents(chunks, embeddings, index_name=index_name)
        print("created index")

  def generate_questions(self, query = "Generate 5 MCQS based on the content of this PDF."):
      if self.vector_store is None:
            raise ValueError("Vector store is not initialized.")
      llm = ChatOpenAI(temperature=1, model_name="gpt-3.5-turbo")
      retriever = self.vector_store.as_retriever(search_type='similarity', search_kwargs={'k': 3})
      chain = RetrievalQA.from_chain_type(llm=llm, chain_type='stuff', retriever=retriever)
      answer = chain.run(query)
      print(f"Answer: {answer}")
      return answer

  def process_pdf(self, uploaded_file):
      pdf_data = self.load_pdf_document(uploaded_file)
      pdf_chunks = self.chunk_pdf_data(pdf_data)
      print("chunk done")
      self.delete_pinecone_index()
      self.insert_or_fetch_embeddings(index_name="photosynthesis", chunks=pdf_chunks)
      answer = self.generate_questions()
      return answer

  








