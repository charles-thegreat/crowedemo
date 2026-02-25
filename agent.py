# agent.py
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.tools import tool
from langchain.agents import create_agent
from pinecone import Pinecone
import os

# Setup
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
embeddings = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=512)

vector_store = PineconeVectorStore(index=pc.Index("crowedemo"), embedding=embeddings)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Retrieve information to help answer a query."""
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs


@tool("calculator", description="Performs arithmetic calculations. Use this for any math problems.")
def calc(expression: str) -> str:
    """Evaluate mathematical expressions."""
    return str(eval(expression))


prompt = """You are a helpful assistant with access to a knowledge base.
    Answer questions accurately using the knowledge base.
    If you don't know the answer, say so - don't make things up."""

tools = [retrieve_context, calc]
agent = create_agent(llm, tools, system_prompt=prompt, name='crowedemo-agent')
def chat(message, history=[]):
    """Run the agent"""
    messages = history + [("user", message)]
    response = agent.invoke({"messages": messages})
    return response["messages"][-1].content