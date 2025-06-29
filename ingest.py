import os
import glob
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# ✅ Load all .txt files
def load_documents(folder_path="./docs"):
    filepaths = glob.glob(os.path.join(folder_path, "*.txt"))
    documents = []
    for path in filepaths:
        print(f"📄 Loading: {path}")
        loader = TextLoader(path, encoding='utf-8')
        loaded_docs = loader.load()
        print(f"✅ Loaded {len(loaded_docs)} docs from {path}")
        documents.extend(loaded_docs)
    return documents

# ✅ Split text
def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
    )
    chunks = splitter.split_documents(documents)
    print(f"🔢 Total chunks created: {len(chunks)}")
    return chunks

# ✅ Embedding and FAISS
def build_faiss_index(chunks, persist_path="faiss_index"):
    if not chunks:
        print("⚠️ No chunks to index. Exiting.")
        return
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(persist_path)
    print(f"📦 Vectorstore saved to {persist_path}")

# ✅ Run all steps
if __name__ == "__main__":
    print("🔍 Loading documents...")
    docs = load_documents()

    print("✂️ Splitting into chunks...")
    chunks = split_documents(docs)

    print("📦 Building FAISS vectorstore...")
    build_faiss_index(chunks)

    print("🚀 Ingestion complete.")
