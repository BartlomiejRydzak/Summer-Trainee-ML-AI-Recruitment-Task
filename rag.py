from chromadb import Client
import os
from dotenv import load_dotenv
load_dotenv()
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from langchain_community.document_loaders import TextLoader

loader = TextLoader("sample.xml")
data = loader.load()

query = "Which documents are related to ML/AI."

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_nvidia_ai_endpoints import ChatNVIDIA

text_splitter = CharacterTextSplitter(
    separator = '>',
    chunk_size = 300,  
    chunk_overlap = 50 
)

chunks = text_splitter.split_documents(data)

embedding_model = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')

vector_store = Chroma.from_documents(
    documents=chunks,
    embedding=embedding_model
)

prompt = """
Use only the context provided to answer the following question.
Context: {context}
Question: {question}
"""

prompt_template = ChatPromptTemplate.from_template(prompt)

llm = ChatNVIDIA(
  model="openai/gpt-oss-120b",
  api_key=os.getenv("nvidia"), 
  temperature=0.1
)

retriever = vector_store.as_retriever(
    search_type='similarity',
    search_kwargs={ "k": 15}
)

chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt_template
    | llm
    | StrOutputParser()
)

result = chain.invoke(query)
print("Result:")
print(result)