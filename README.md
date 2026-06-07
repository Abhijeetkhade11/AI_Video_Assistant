# AI Video Assistant

> Lightweight local pipeline to transcribe, summarize, and run RAG-based Q&A over meeting/video audio.

## Features
- Download or accept local audio/video input and split into processable chunks
- Local Whisper transcription (PyTorch)
- Summarization, title generation, and extraction of action items / decisions / questions
- Vector store (Chroma) with HuggingFace embeddings for RAG-style question answering
- Streamlit UI and a CLI entrypoint

## Quick Start
Prerequisites:
- Python 3.10+
- FFmpeg installed and available on PATH (for audio processing)
- A virtual environment is recommended

1. Create and activate a virtual environment
```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
```
2. Install Python dependencies
```powershell
pip install -r requirements.txt
```

Note about PyTorch and torchvision

The project uses local Whisper (which depends on PyTorch) and some Hugging Face packages that may import vision helpers. If you encounter errors like "No module named 'torchvision'", install a matching set of PyTorch packages for your platform. For a CPU-only Windows install, one simple option is:

```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

If you have an NVIDIA GPU, follow the official PyTorch install selector at https://pytorch.org/get-started/locally to pick the correct CUDA-enabled wheels.

## Environment variables
Create a `.env` file in the project root with any required keys. Currently used variables:
- `MISTRAL_API_KEY` — API key for the Mistral LLM (used by the RAG/chat portion)

## Running
- Run the Streamlit app:
```powershell
streamlit run app.py
```
- Run the CLI pipeline (interactive):
```powershell
python main.py
```

## Project Structure
- `app.py` — Streamlit UI entrypoint
- `main.py` — CLI entrypoint
- `core/` — Core pipeline modules
  - `transcriber.py` — Transcription orchestration
  - `summarize.py` — Summarization and title generation
  - `extractor.py` — Action-item / decision / question extraction
  - `rag_engine.py` — RAG pipeline and LLM orchestration
  - `vector_store.py` — Chroma vector store + embeddings
- `utils/` — Utility helpers (audio processing, file handling)
- `vector_db/` — Persisted Chroma DB files

## Troubleshooting
- ModuleNotFoundError: No module named 'torchvision' — install `torchvision` matching your `torch` version (see note above).
- FFmpeg errors — ensure FFmpeg binary is installed and on your PATH.

## License
This project is provided as-is. Add a license file if you plan to publish.
