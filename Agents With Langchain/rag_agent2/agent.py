import os
import chromadb
from langchain_chroma import Chroma
from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm  # Verified path
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

# Load environment variables
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
# GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# --- CHROMA CLOUD CONFIGURATION ---
CHROMA_TENANT = 'ghulam_sarwar_work'.strip()
CHROMA_DB_NAME = 'default'.strip()
CHROMA_API_KEY = os.environ.get("CHROMADB_API_KEY").strip()

# Tool for RAG
def rag_tool(query: str) -> str:
    """Consult this tool for official company policy information."""
    
    # 1. Initialize Chroma Cloud Client
    cloud_client = chromadb.CloudClient(
        tenant=CHROMA_TENANT,
        database=CHROMA_DB_NAME,
        api_key=CHROMA_API_KEY
    )

    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_KEY)

    # 2. Connect LangChain to Cloud Collection
    # Note: 'persist_directory' is NOT used for CloudClient
    vectorstore = Chroma(
        client=cloud_client,
        collection_name="company_policy_collection", # Name this as you like
        embedding_function=embeddings
    )

    # 3. Check if we need to upload data (Only if cloud is empty)
    if vectorstore._collection.count() == 0:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, "company_policy.txt")
        
        if not os.path.exists(file_path):
            return "Error: Local policy file not found for initial upload."

        loader = TextLoader(file_path)
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_documents(docs)
        
        # Add documents to the cloud
        vectorstore.add_documents(documents=chunks)

    # 4. Standard RAG logic
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    llm = ChatOpenAI(model="gpt-4o", temperature=0, openai_api_key=OPENAI_KEY)
    
    system_instructions = (
        "Use the following context to answer. "
        "If unsure, say you don't know.\n\nContext: {context}"
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_instructions),
        ("human", "{input}"),
    ])

    combine_docs_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, combine_docs_chain)

    response = rag_chain.invoke({"input": query})
    return response['answer']

# --- Main LLM Agent ---
openai_model = LiteLlm(model="openai/gpt-4o", api_key=OPENAI_KEY)

root_agent = LlmAgent(
    model=openai_model,
    name='root_agent',
    description='A helpful assistant for policy questions.',
    instruction="Always use rag_tool for HR or policy queries.",
    tools=[rag_tool]
)