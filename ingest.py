import os
import glob
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

def safe_read_file(file_path):
    """Safely read a file with encoding error handling"""
    try:
        # Try UTF-8 with error handling
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return None

def load_documents(folder_path="./docs"):
    print(f"🔍 Looking for files in: {os.path.abspath(folder_path)}")
    
    if not os.path.exists(folder_path):
        print(f"❌ Folder {folder_path} doesn't exist!")
        return []
    
    filepaths = glob.glob(os.path.join(folder_path, "*.txt"))
    print(f"📋 Found {len(filepaths)} .txt files")
    
    documents = []
    
    for path in filepaths:
        print(f"📖 Loading: {path}")
        
        # Read file safely
        content = safe_read_file(path)
        if content is None:
            continue
            
        if len(content.strip()) == 0:
            print(f"⚠️  File is empty, skipping...")
            continue
        
        # Create a temporary clean file
        temp_path = path + ".clean"
        try:
            # Write cleaned content to temp file
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Load using LangChain
            loader = TextLoader(temp_path, encoding="utf-8")
            docs = loader.load()
            documents.extend(docs)
            
            # Clean up temp file
            os.remove(temp_path)
            
            print(f"✅ Loaded {path} ({len(content)} chars, {len(docs)} documents)")
            
        except Exception as e:
            print(f"❌ Failed to load {path}: {e}")
            # Clean up temp file if it exists
            if os.path.exists(temp_path):
                os.remove(temp_path)
            continue
    
    return documents

def split_documents(documents):
    if not documents:
        print("❌ No documents to split!")
        return []
        
    print(f"✂️ Splitting {len(documents)} documents...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
    )
    chunks = splitter.split_documents(documents)
    
    print(f"📝 Created {len(chunks)} chunks")
    if chunks:
        print(f"📄 Sample chunk: {chunks[0].page_content[:100]}...")
    
    return chunks

def build_faiss_index(chunks, persist_path="faiss_index"):
    if not chunks:
        print("❌ No chunks to index!")
        return
        
    print(f"🤖 Loading HuggingFace embeddings...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    print(f"🏗️ Building FAISS index from {len(chunks)} chunks...")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    
    print(f"💾 Saving to {persist_path}...")
    vectorstore.save_local(persist_path)
    print(f"✅ Index saved to {persist_path}")

if __name__ == "__main__":
    print("🚀 Starting document ingestion...")
    
    docs = load_documents()
    print(f"\n📊 Loaded {len(docs)} documents total")
    
    if len(docs) == 0:
        print("❌ No documents loaded! Check your ./docs folder")
        exit(1)
    
    chunks = split_documents(docs)
    
    if len(chunks) == 0:
        print("❌ No chunks created!")
        exit(1)
    
    build_faiss_index(chunks)
    print("\n🎉 Successfully created FAISS index!")