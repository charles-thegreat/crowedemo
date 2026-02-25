# ingest.py
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
import os
from pinecone import Pinecone
from uuid import uuid4
from langchain_core.documents import Document

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Load documents (use sample PDFs or make txt files)
loader = DirectoryLoader("./documents", glob="**/*.txt")
docs = loader.load()

# Chunk
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
chunks = splitter.split_documents(docs)

# Embed and upload
embeddings = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=512)
index = pc.Index(name = 'crowedemo')
vectorstore = PineconeVectorStore(index=index, embedding=embeddings)

document_1 = Document(
    page_content="I had chocolate chip pancakes and scrambled eggs for breakfast this morning.",
    metadata={"source": "tweet"},
)
documents = [document_1]
vectorstore.add_documents(documents=documents, ids=[str(uuid4())])
print(f"Uploaded {len(documents)} documents")