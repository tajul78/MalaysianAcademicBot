import os
import glob
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings


# Load documents from ./docs folder
def load_documents(folder_path="./docs"):
    filepaths = glob.glob(os.path.join(folder_path, "*.txt"))
    documents = []
    for path in filepaths:
        loader = TextLoader(path, encoding="utf-8")
        documents.extend(loader.load())
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
    embeddings = HuggingFaceEmbeddings()  # No API key needed
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
