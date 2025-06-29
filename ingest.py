# ingest.py

import os
import glob
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# 🔹 Load .txt documents from /docs
def load_documents(folder_path="./docs"):
    filepaths = glob.glob(os.path.join(folder_path, "*.txt"))
    documents = []

    for path in filepaths:
        try:
            loader = TextLoader(path)
            documents.extend(loader.load())
        except Exception as e:
            print(f"⚠️ Error loading {path}: {e}")
    
    return documents

# 🔹 Chunk documents into overlapping blocks
def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
    )
    return splitter.split_documents(documents)
    
chunks = split_documents(docs)
print(f"🔢 {len(chunks)} chunks created.")
if not chunks:
    print("❌ No chunks generated. Possible empty .txt files or bad encoding.")
    exit()

# 🔹 Embed and save to FAISS vectorstore
def build_faiss_index(chunks, persist_path="faiss_index"):
    if not chunks:
        print("❌ No chunks to index. Check your input files.")
        return

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(persist_path)
    print(f"✅ FAISS index saved to: {persist_path}")

# 🔹 Run everything
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
