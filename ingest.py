# ingest.py

import os
import glob
import pickle
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Load PDF documents from ./docs folder
def load_documents(folder_path="./docs"):
    loader = DirectoryLoader(
        path=folder_path,
        glob="**/*.pdf",
        loader_cls=PyPDFLoader
    )
    documents = loader.load()
    return documents

# Split text into chunks
def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
    )
    return splitter.split_documents(documents)

# Embed and store in FAISS
def build_faiss_index(chunks, persist_path="faiss_index"):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(persist_path)
    print(f"✅ Index saved to {persist_path}")

if __name__ == "__main__":
    print("🔍 Loading documents...")
    docs = load_documents()
    print(f"📄 {len(docs)} documents loaded.")

    print("✂️ Splitting into chunks...")
    chunks = split_documents(docs)
    print(f"🔢 {len(chunks)} chunks created.")

    print("📦 Building FAISS vectorstore...")
    build_faiss_index(chunks)
    print("🚀 Done.")
