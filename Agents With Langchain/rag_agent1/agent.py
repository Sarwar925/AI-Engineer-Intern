import os
from langchain_chroma import Chroma
from dotenv import load_dotenv  # Add this import
from google.adk.agents.llm_agent import LlmAgent
from google.adk.models import LiteLlm
# Import necessary modules for RAG
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

# Load environment variables from .env file
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

# Tool for RAG
def rag_tool(query: str) -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "company_policy.txt")
    
    # Check if file exists before trying to load it
    if not os.path.exists(file_path):
        return f"System Error: The policy file was not found at {file_path}"
    # 1. Load the Document
    loader = TextLoader(file_path)
    docs = loader.load()

    # 2. Split Text into manageable chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(docs)

    # 3. Create Vector Store (The "Brain")
    embeddings = OpenAIEmbeddings()
    persist_directory = os.path.join(base_dir, "chroma_db")
    vectorstore = Chroma.from_documents(
            documents=chunks, 
            embedding=embeddings, 
            persist_directory=persist_directory
        )
    retriever = vectorstore.as_retriever()

    # 4. Define the AI's Behavior
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    system_instructions = (
        "Use the following pieces of context to answer the question. "
        "If you don't know the answer, just say you don't know.\n\n"
        "Context: {context}"
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_instructions),
        ("human", "{input}"),
    ])

    # 5. Build and Run the Chain
    combine_docs_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, combine_docs_chain)

    # 6. Get the Answer
    response = rag_chain.invoke({"input": query})
    return response['answer']

# Main LLM Agent
openai_model = LiteLlm(model="openai/gpt-4o", api_key=OPENAI_KEY)

root_agent = LlmAgent(
    model=openai_model,
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction="Use this tool to retrieve specific information from the company's official policy documentation. This tool is essential for answering questions regarding remote work rules, vacation days, office hours, and employee conduct. You must consult this tool before providing any specific policy-related answers to ensure accuracy.If you don't find tool related information then say I don't know.",
    tools=[rag_tool]
)
