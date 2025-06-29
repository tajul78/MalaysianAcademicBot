# ingest.py

import os
import glob
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Step 1: Load all PDF files from ./docs folder
def load_documents(folder_path="./docs"):
    filepaths = glob.glob(os.path.join(folder_path, "*.pdf"))
    documents = []
    for path in filepaths:
        loader = UnstructuredPDFLoader(path)
        documents.extend(loader.load())
    return documents

# Step 2: Split documents into chunks
def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
    )
    return splitter.split_documents(documents)

# Step 3: Embed chunks and store using FAISS
def build_faiss_index(chunks, persist_path="faiss_index"):
    if not chunks:
        print("⚠️ No chunks to index. Please check your PDF content.")
        return
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(persist_path)
    print(f"✅ Index saved to {persist_path}")

# Entry point
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
