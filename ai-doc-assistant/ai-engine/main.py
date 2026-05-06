import argparse
import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_chroma import Chroma

from langchain_community.document_loaders import PyPDFLoader
from langchain_classic.chains import RetrievalQA

load_dotenv()

DEFAULT_PERSIST_DIRECTORY = "./chroma_db"

class DocumentAssistant:
    def __init__(self, persist_directory: str = DEFAULT_PERSIST_DIRECTORY):
        # Pointing to the local model running in Ollama
        self.llm = OllamaLLM(model="llama3") 
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        self.persist_directory = persist_directory
        self.vector_db = None
        
    def ingest_document(self, file_path: str):
        """Chunk the PDF and build the vector store."""
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        loader = PyPDFLoader(file_path)
        pages = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = splitter.split_documents(pages)

        self.vector_db = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
        )

        print(f"Ingested {len(chunks)} chunks from {file_path}")
        return len(chunks)

    def load_vector_store(self):
        """Load an existing Chroma index from disk if it exists."""
        if not os.path.isdir(self.persist_directory):
            return False

        self.vector_db = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
        )
        return True

    def ask_question(self, query: str):
        """Answer a query and return both the answer and the source metadata."""
        if not self.vector_db:
            raise RuntimeError("Vector store not initialized.")

        # 1. Retrieve the top 'k' chunks manually
        retriever = self.vector_db.as_retriever(search_kwargs={"k": 3})
        docs = retriever.invoke(query)
        
        # 2. Combine context and extract unique sources
        context_text = "\n\n".join([doc.page_content for doc in docs])
        sources = set([doc.metadata.get("source", "Unknown") for doc in docs])
        
        # 3. Create a custom prompt that forces citation
        prompt = f"""
        You are a helpful assistant. Use the following context to answer the question.
        If you don't know the answer, just say you don't know.
        
        Context:
        {context_text}
        
        Question: {query}
        """
        
        # 4. Generate the answer
        answer = self.llm.invoke(prompt)
        
        # 5. Return a structured dictionary
        return {
            "answer": answer,
            "sources": list(sources)
        }


def parse_args():
    parser = argparse.ArgumentParser(description="Document assistant for PDF retrieval QA.")
    parser.add_argument("--pdf", help="Path to the PDF file to ingest.")
    parser.add_argument("--query", help="Question to ask after ingesting or loading the document.")
    parser.add_argument(
        "--persist-dir",
        default=DEFAULT_PERSIST_DIRECTORY,
        help="Directory where Chroma stores embeddings and metadata.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    assistant = DocumentAssistant(persist_directory=args.persist_dir)

    if args.pdf:
        assistant.ingest_document(args.pdf)
    elif not assistant.load_vector_store():
        raise SystemExit("No PDF was provided and the vector store does not exist. Use --pdf to ingest a document.")

    if args.query:
        answer = assistant.ask_question(args.query)
        print("\nAnswer:\n", answer)
    else:
        print("Document loaded. Use --query to ask a question.")