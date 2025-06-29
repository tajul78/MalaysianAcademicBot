import os
import glob
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# 1. Load all .txt documents from ./docs
def load_documents(folder_path="./docs"):
    filepaths = glob.glob(os.path.join(folder_path, "*.txt"))
    documents = []
    for path in filepaths:
        loader = TextLoader(path)
        documents.extend(loader.load())
    return documents

# 2. Split documents into chunks
def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
    )
    return splitter.split_documents(documents)

# 3. Create FAISS vector index from chunks
def build_faiss_index(chunks, persist_path="faiss_index"):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(persist_path)
    print(f"✅ FAISS index saved to '{persist_path}'")

# 4. Run everything
if __name__ == "__main__":
    print("🔍 Loading .txt documents from ./docs...")
    docs = load_documents()
    print(f"📄 {len(docs)} documents loaded.")

    print("✂️ Splitting into chunks...")
    chunks = split_documents(docs)
    print(f"🔢 {len(chunks)} chunks created.")

    print("📦 Building FAISS vectorstore...")
    build_faiss_index(chunks)
    print("🚀 Done.")
