import os

vector_store = None

def process_pdf(uploaded_file):
    pdf_data = load_pdf_document(uploaded_file)
    pdf_chunks = chunk_pdf_data(pdf_data)
    delete_pinecone_index()

    global vector_store 
    vector_store = insert_or_fetch_embeddings(index_name="photosynthesis", chunks=pdf_chunks)


def answer_query(query):
  from langchain.chains import RetrievalQA
  from langchain.chat_models import ChatOpenAI

  llm = ChatOpenAI(temperature=1, model_name="gpt-3.5-turbo")
  retriever = vector_store.as_retriever(search_type='similarity', search_kwargs={'k': 3})
  chain = RetrievalQA.from_chain_type(llm=llm, chain_type='stuff', retriever=retriever)
  answer = chain.run(query)
  return answer

def insert_or_fetch_embeddings(index_name, chunks):
  import pinecone
  from langchain_community.vectorstores import Pinecone
  from langchain_openai import OpenAIEmbeddings
  from pinecone import PodSpec
  from pinecone import ServerlessSpec

  pc = pinecone.Pinecone()
  embeddings = OpenAIEmbeddings(model = 'text-embedding-3-small', dimensions=1536)

  if index_name in pc.list_indexes().names():
    print(f'Index name: {index_name} already exists, loading embeddings')
    vector_store = Pinecone.from_existing_index(index_name,embeddings)
    print("fetched index")
  else:
    print(f"Creating Index: {index_name} and embeddings")
    #pc.create_index(name=index_name, dimension=1536, metric='cosine', spec = PodSpec(environment='gcp-starter'))
    pc.create_index(
       name = index_name,
       dimension = 1536,
       metric = 'cosine',
       spec = ServerlessSpec(
          cloud = 'aws',
          region = 'us-east-1'
       )
    )
    vector_store = Pinecone.from_documents(chunks, embeddings, index_name=index_name)
    print("created index")

  return vector_store

def delete_pinecone_index(index_name='all'):
  import pinecone
  pc = pinecone.Pinecone()
  if index_name == 'all':
    indexes = pc.list_indexes().names()
    print("Deleting all indices")
    for index in indexes:
      pc.delete_index(index)

  else:
    pc.delete_index(index_name)

def chunk_pdf_data(pdf_data):
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1024, chunk_overlap = 0)
    chunks = text_splitter.split_documents(pdf_data)
    return chunks

def load_pdf_document(uploaded_file):
    # Check if the uploaded file is a PDF
    if uploaded_file.type == "application/pdf":
        from langchain.document_loaders import PyPDFLoader
        
        # Save the uploaded file to a temporary location
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Load the PDF file
        loader = PyPDFLoader(uploaded_file.name)
        data = loader.load()

        # Remove the temporary file after loading
        os.remove(uploaded_file.name)
        
        return data
