# 🧠 RAG Chatbot (Streamlit + LangChain + Groq)

A powerful Retrieval-Augmented Generation (RAG) chatbot that lets you chat with your **PDFs and websites** using LLMs.

Built using:
- 🧩 Streamlit (UI)
- 🔗 LangChain (RAG pipeline)
- ⚡ Groq (LLaMA 3.1)
- 🧠 HuggingFace Embeddings
- 📚 ChromaDB (Vector Database)

---

# 🚀 Features

- 📄 Upload multiple PDF files
- 🌐 Add multiple website URLs
- 💬 Chat with your documents
- 🧠 Context-aware responses (RAG)
- 📊 Source tracking & citations
- 🔄 Session-based memory
- ⚡ Fast inference using Groq

---

# 📦 Project Structure

---

# ⚙️ Requirements

- Python **3.10 recommended**

---

# 🔐 Environment Setup

Create a `.env` file in the root directory and add the following keys:

```env
OPENAI_API_KEY="your_openai_api_key_here"

LANGSMITH_API_KEY="your_langsmith_api_key_here"

LANGCHAIN_PROJECT="GENAI_APP_WITH_OPENAI"

GROQ_API_KEY="your_groq_api_key_here"

HF_TOKEN="your_huggingface_token_here"

# ▶️ Run Application

To start the Streamlit app, run:

```bash
streamlit run app.py