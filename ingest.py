import os
import glob
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def load_documents(folder_path="./docs"):
    filepaths = glob.glob(os.path.join(folder_path, "*.pdf"))
    print(f"📁 Found {len(filepaths)} PDF files.")
    documents = []
    for path in filepaths:
        print(f"📄 Loading: {path}")
        loader = PyPDFLoader(path)
        pages = loader.load()
        if pages:
            print(f"✅ Loaded {len(pages)} pages from {os.path.basename(path)}")
        else:
            print(f"⚠️ Warning: No text extracted from {os.path.basename(path)}")
        documents.extend(pages)
    return documents

def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    chunks = splitter.split_documents(documents)
    print(f"🔢 Total chunks created: {len(chunks)}")
    if chunks:
        print("📌 Sample chunk preview:\n", chunks[0].page_content[:300])
    return chunks

def build_faiss_index(chunks, persist_path="faiss_index"):
    if not chunks:
        print("❌ No chunks to embed. Aborting.")
        return
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(persist_path)
    print(f"✅ Vectorstore saved at '{persist_path}'")

if __name__ == "__main__":
    print("🔍 Loading documents...")
    docs = load_documents()

    if not docs:
        print("❌ No documents loaded. Exiting.")
        exit()

    print("✂️ Splitting into chunks...")
    chunks = split_documents(docs)

    print("📦 Building FAISS vectorstore...")
    build_faiss_index(chunks)

    print("🚀 Done.")
