# AI Document Assistant

A lightweight PDF retrieval assistant using Chroma, OpenAI embeddings, and LangChain.

## Setup

1. Activate your Python environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your OpenAI API key:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```
```

## Usage

Ingest a PDF and ask a question:

```bash
python main.py --pdf path/to/document.pdf --query "Summarize the main points."
```

Load an existing vector store and ask a query:

```bash
python main.py --query "What is the main topic?"
```

## Notes

- The default Chroma persist directory is `./chroma_db`.
- Use `--persist-dir` to change where embeddings are stored.
