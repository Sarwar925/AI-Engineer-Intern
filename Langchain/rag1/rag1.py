# RAG1: Building a Retrieval-Augmented Generation (RAG) System with LangChain
import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

# 1. API Key Setup
os.environ["OPENAI_API_KEY"] = "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" 

# 2. Load the Document
loader = TextLoader("company_policy.txt")
docs = loader.load()

# 3. Split Text into manageable chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_documents(docs)

# 4. Create Vector Store (The "Brain")
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(chunks, embeddings)
retriever = vectorstore.as_retriever()

# 5. Define the AI's Behavior
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

# 6. Build and Run the Chain
combine_docs_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, combine_docs_chain)

# 7. Get the Answer
response = rag_chain.invoke({"input": "What is the time right now?"})
print(f"\nAI Answer: {response['answer']}")