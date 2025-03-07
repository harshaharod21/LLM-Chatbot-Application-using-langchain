import streamlit as st
import os
import ollama
from langchain_groq import ChatGroq                               # Inference engine
from langchain_community.document_loaders import WebBaseLoader    # Data Ingestion
from langchain.embeddings import OllamaEmbeddings                 # Open source embedding
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
import time


from dotenv import load_dotenv
load_dotenv()

## Load the groq API Key

groq_api_key= os.environ['GROQ_API_KEY']

if "vector" not in st.session_state:
    st.session_state.embeddings=OllamaEmbeddings(model='nomic-embed-text')
    st.session_state.loader=WebBaseLoader("https://towardsdatascience.com/llm-evals-setup-and-the-metrics-that-matter-2cc27e8e35f3")  #different data ingestion ways are present
    st.session_state.docs= st.session_state.loader.load()

    st.session_state.text_splitter= RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)   #different ways to split the text ae present
    st.session_state.final_documents= st.session_state.text_splitter.split_documents(st.session_state.docs) #can take only n docs 
    st.session_state.vectors=FAISS.from_documents(st.session_state.final_documents,st.session_state.embeddings)

st.title("Chat with Groq")
llm= ChatGroq(groq_api_key=groq_api_key,
              model_name='llama3-70b-8192')

prompt= ChatPromptTemplate.from_template(

"""
Answer the questions based on the provided context only.
Please provide the most accurate response based on the question
<context>
{context}
<context>
Question: {input}
"""
)

document_chain= create_stuff_documents_chain(llm,prompt)
retriever= st.session_state.vectors.as_retriever()
retrieval_chain= create_retrieval_chain(retriever, document_chain)

prompt=st.text_input('Input your prompt here: ')

if prompt:
    start=time.process_time()
    response= retrieval_chain.invoke({"input":prompt}) 
    print("Response time: ",time.process_time()-start)
    st.write(response['answer'])

    #with streamlit expander

    with st.expander("Document Similarity Search"):
        #Find the relevant chunks
        for i,doc in enumerate(response["context"]):
            st.write(doc.page_content)
            st.write("-----------------------------------")




