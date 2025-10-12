import os
import openai
import pinecone
from pdfminer.high_level import extract_text

from dotenv import load_dotenv
from pathlib import Path
import time

load_dotenv(dotenv_path=Path("/Users/Roger/Documents/PersonalProject/Job Automation/.env"))

openai.api_key = os.environ["OPENAI_API_KEY"]

# Initialize Pinecone client with new API
pc = pinecone.Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index = pc.Index("roger-resume")

def chunk_text(text, chunk_size=800):
    """Split long text into manageable pieces"""
    words = text.split()
    return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

def embed_and_upload(file_path, user_id):
    """Embed a single file and upload to Pinecone"""
    file_ext = Path(file_path).suffix.lower()
    
    # Extract text based on file type
    if file_ext == '.pdf':
        text = extract_text(file_path)
    elif file_ext in ['.txt', '.md']:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    elif file_ext in ['.docx', '.doc']:
        try:
            from docx import Document
            doc = Document(file_path)
            text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        except ImportError:
            print(f"❌ python-docx not installed. Install with: pip install python-docx")
            raise
    else:
        raise ValueError(f"Unsupported file type: {file_ext}")
    
    chunks = chunk_text(text)

    for i, chunk in enumerate(chunks):
        emb = openai.embeddings.create(
            model="text-embedding-3-large",
            input=chunk
        )
        vector = emb.data[0].embedding

        index.upsert(vectors=[{
            "id": f"{os.path.basename(file_path)}-{i}",
            "values": vector,
            "metadata": {"text": chunk, "source": os.path.basename(file_path)}
        }], namespace=user_id)
        time.sleep(0.3)  # prevent hitting API rate limit

    print(f"✅ Uploaded {len(chunks)} chunks from {file_path} to namespace {user_id}")

# Option 1: Simple Loop - Embed multiple files at once
if __name__ == "__main__":
    # List of files to embed
    files_to_embed = [
        "/Users/Roger/Documents/FullTime-Resume/Resume Template - One Page/AI_Feed/resume.txt",
        "/Users/Roger/Documents/FullTime-Resume/Resume Template - One Page/AI_Feed/Roger Xu_Fullstack_Resume.docx",
        "/Users/Roger/Documents/FullTime-Resume/Resume Template - One Page/AI_Feed/Roger Xu_Frontend_Resume.docx",
        "/Users/Roger/Documents/FullTime-Resume/Resume Template - One Page/AI_Feed/Roger Xu_SharePoint_Resume.docx",
        "/Users/Roger/Documents/FullTime-Resume/Resume Template - One Page/AI_Feed/Rong Gang Xu_Resume_v3.docx",
        "/Users/Roger/Documents/FullTime-Resume/Resume Template - One Page/AI_Feed/Other_things.txt",
        # Add more files as needed
    ]
    
    user_id = "roger"  # Your user identifier
    
    print(f"🚀 Starting to embed {len(files_to_embed)} files...")
    
    # Embed each file
    for file_path in files_to_embed:
        try:
            print(f"📄 Processing: {os.path.basename(file_path)}")
            embed_and_upload(file_path, user_id)
            print(f"✅ Successfully embedded: {os.path.basename(file_path)}")
        except Exception as e:
            print(f"❌ Failed to embed {os.path.basename(file_path)}: {e}")
    
    print(f"🎉 Finished processing all files!")
