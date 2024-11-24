import os
import streamlit as st
import pickle
import time
from langchain_community.llms import OpenAI
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env
llm = OpenAI(OPENAI_API_KEY="OPENAI_API_KEY")
st.title("URL FETCHER")
st.sidebar.title("Study Article URLs")

# Initialize session state for URLs
if 'urls' not in st.session_state:
    st.session_state.urls = [""] * 3  # Start with three empty URL fields

# Dynamic URL input handling
for i in range(len(st.session_state.urls)):
    st.session_state.urls[i] = st.sidebar.text_input(f"URL {i + 1}", st.session_state.urls[i])

if st.sidebar.button("Add Another URL"):
    st.session_state.urls.append("")  # Add a new URL input field

process_url_clicked = st.sidebar.button("Process URLs")
file_path = "faiss_store_openai.pkl"
main_placeholder = st.empty()
llm = OpenAI(temperature=0.9, max_tokens=500)

def load_and_process_data(urls):
    try:
        loader = UnstructuredURLLoader(urls=urls)
        main_placeholder.text("Data Loading...Started...✅")
        data = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            separators=['\n\n', '\n', '.', ','],
            chunk_size=1000
        )
        main_placeholder.text("Text Splitter...Started...✅")
        docs = text_splitter.split_documents(data)
        
        embeddings = OpenAIEmbeddings()
        vectorstore_openai = FAISS.from_documents(docs, embeddings)
        main_placeholder.text("Embedding Vector Started Building...✅")
        
        # Save the FAISS index to a pickle file
        with open(file_path, "wb") as f:
            pickle.dump(vectorstore_openai, f)
        
        main_placeholder.text("Data Processing Complete! ✅")
        
    except Exception as e:
        main_placeholder.error(f"Error occurred: {e}")

if process_url_clicked:
    load_and_process_data(st.session_state.urls)

query = main_placeholder.text_input("Question: ")
if query:
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            vectorstore = pickle.load(f)
            chain = RetrievalQAWithSourcesChain.from_llm(llm=llm, retriever=vectorstore.as_retriever())
            result = chain({"question": query}, return_only_outputs=True)
            
            # Result will be a dictionary of this format --> {"answer": "", "sources": [] }
            st.header("Answer")
            st.write(result["answer"])

            # Display sources, if available
            sources = result.get("sources", "")
            if sources:
                st.subheader("Sources:")
                sources_list = sources.split("\n")  # Split the sources by newline
                for source in sources_list:
                    st.write(source)
