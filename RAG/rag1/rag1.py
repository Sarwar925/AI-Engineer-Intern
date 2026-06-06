import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import logging
logging.basicConfig(level=logging.INFO,filename="log",filemode='a')
# ==========================================
# 1. CONFIGURATION (Replace with your keys)
# ==========================================
import dotenv
dotenv.load_dotenv()  # Load variables from .env file
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")  # Your OpenAI Key

# Chroma Cloud Details
CHROMA_API_KEY = os.environ.get("CHROMA_API_KEY")             # From your Chroma Dashboard
CHROMA_TENANT = os.environ.get("CHROMA_TENANT")
CHROMA_DATABASE = os.environ.get("CHROMA_DATABASE")
COLLECTION_NAME = "Langchain-1"

# ==========================================
# 2. INGESTION (File -> Chunks -> Cloud)
# ==========================================
print("--- Starting Ingestion ---")

# Load the file
loader = PyPDFLoader("privacy_policy.pdf")  # Make sure this file is in your folder
raw_docs = loader.load()

# Split into manageable pieces
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = text_splitter.split_documents(raw_docs)
print(len(chunks))
# Initialize Embeddings
embeddings = OpenAIEmbeddings()
logging.info(embeddings)
# Create Vector Store & Upload to Chroma Cloud
vector_store = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    collection_name=COLLECTION_NAME,
    chroma_cloud_api_key=CHROMA_API_KEY,
    tenant=CHROMA_TENANT,
    database=CHROMA_DATABASE
)

print(f"--- Success: {len(chunks)} chunks uploaded to Chroma Cloud ---")

# ==========================================
# 3. RETRIEVAL & GENERATION (The RAG Chain)
# ==========================================

# Setup the retriever (finds top 3 relevant chunks)
retriever = vector_store.as_retriever(search_kwargs={"k": 3})

# Define the AI logic (Prompt)
template = """Answer the question based ONLY on the following context:
{context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Build the Chain
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# ==========================================
# 4. EXECUTION
# ==========================================
query = "What is the policy of work from home?"
print(f"\nUser Question: {query}")

response = rag_chain.invoke(query)

print("\n--- AI RESPONSE ---")
print(response)

