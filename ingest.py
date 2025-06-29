import os
import glob
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Load environment variables (especially GOOGLE_API_KEY)
load_dotenv()

# Load PDFs from ./docs folder
def load_documents(folder_path="./docs"):
    filepaths = glob.glob(os.path.join(folder_path, "*.pdf"))
    documents = []
    for path in filepaths:
        loader = PyPDFLoader(path)
        documents.extend(loader.load())
    return documents

# Split into chunks
def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    return splitter.split_documents(documents)

# Build and save FAISS index
def build_faiss_index(chunks, persist_path="faiss_index"):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    if not chunks:
        raise ValueError("No chunks found. Cannot build index.")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(persist_path)
    print(f"✅ FAISS index saved at: {persist_path}")

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
