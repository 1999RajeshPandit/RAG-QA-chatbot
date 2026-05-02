import os
import uuid
import tempfile
import requests
import streamlit as st
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# ─── Page config (must be first Streamlit call) ──────────────────────────────
st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Root & base ── */
html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
}

/* ── App background ── */
.stApp {
    background: linear-gradient(135deg, #0d0f1a 0%, #111827 50%, #0d1117 100%);
    min-height: 100vh;
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1623 0%, #131d2e 100%) !important;
    border-right: 1px solid #1e2d42;
}
[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #7dd3fc !important;
}

/* ── Hero header ── */
.hero-header {
    text-align: center;
    padding: 1.5rem 0 0.5rem;
    margin-bottom: 0.5rem;
}
.hero-title {
    font-size: 2.4rem;
    font-weight: 700;
    background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -1px;
    margin-bottom: 0.2rem;
}
.hero-sub {
    color: #64748b;
    font-size: 0.95rem;
    font-weight: 400;
}

/* ── Status pill ── */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: rgba(16,185,129,0.12);
    border: 1px solid rgba(16,185,129,0.35);
    color: #34d399;
    font-size: 0.78rem;
    font-weight: 600;
    padding: 4px 14px;
    border-radius: 999px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin: 6px auto;
}
.status-pill.waiting {
    background: rgba(251,191,36,0.1);
    border-color: rgba(251,191,36,0.3);
    color: #fbbf24;
}

/* ── Source tags ── */
.source-chip {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.3);
    color: #a5b4fc;
    font-size: 0.72rem;
    padding: 2px 10px;
    border-radius: 999px;
    margin: 2px 3px;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Chat container ── */
.chat-wrapper {
    background: rgba(15,23,42,0.6);
    border: 1px solid #1e293b;
    border-radius: 16px;
    padding: 1.2rem 1.5rem;
    backdrop-filter: blur(8px);
    margin-bottom: 1rem;
}

/* ── Message bubbles ── */
[data-testid="stChatMessage"] {
    border-radius: 12px !important;
    margin-bottom: 0.6rem !important;
    padding: 0.8rem 1rem !important;
    border: 1px solid transparent;
}
[data-testid="stChatMessage"][data-testid*="user"],
div[data-testid="stChatMessage"]:has(img[alt="user"]) {
    background: rgba(99,102,241,0.08) !important;
    border-color: rgba(99,102,241,0.2) !important;
}
div[data-testid="stChatMessage"]:has(img[alt="assistant"]) {
    background: rgba(15,23,42,0.5) !important;
    border-color: #1e293b !important;
}

/* ── Input box ── */
[data-testid="stChatInput"] textarea {
    background: #0f172a !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.95rem !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 2px rgba(56,189,248,0.15) !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: rgba(15,23,42,0.6) !important;
    border: 2px dashed #1e3a5f !important;
    border-radius: 12px !important;
    transition: border-color 0.2s;
}
[data-testid="stFileUploader"]:hover {
    border-color: #38bdf8 !important;
}

/* ── Text area (URL input) ── */
.stTextArea textarea {
    background: #0c1220 !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
}

/* ── Buttons ── */
.stButton button {
    background: linear-gradient(135deg, #1d4ed8, #6d28d9) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 0.03em !important;
    transition: all 0.2s !important;
}
.stButton button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(99,102,241,0.4) !important;
}

/* ── Metrics / info cards ── */
.info-card {
    background: rgba(15,23,42,0.7);
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 12px;
}
.info-card .label {
    color: #475569;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 4px;
}
.info-card .value {
    color: #e2e8f0;
    font-size: 1.1rem;
    font-weight: 600;
}

/* ── Divider ── */
hr { border-color: #1e293b !important; }

/* ── Spinner text ── */
.stSpinner p { color: #7dd3fc !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0d0f1a; }
::-webkit-scrollbar-thumb { background: #1e3a5f; border-radius: 4px; }

/* ── Warning / success ── */
.stSuccess { border-radius: 10px !important; }
.stWarning { border-radius: 10px !important; }
.stError   { border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

# ─── Environment setup ────────────────────────────────────────────────────────
load_dotenv()

def setup_env():
    for key in ["LANGCHAIN_TRACING_V2", "LANGCHAIN_ENDPOINT",
                "LANGCHAIN_API_KEY", "LANGCHAIN_PROJECT",
                "GROQ_API_KEY", "HF_TOKEN"]:
        val = os.getenv(key.replace("LANGCHAIN_API_KEY", "LANGSMITH_API_KEY") if key == "LANGCHAIN_API_KEY" else key)
        if val:
            os.environ[key] = val
    os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
    os.environ.setdefault("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
    os.environ.setdefault("LANGCHAIN_PROJECT", "RAG QA Chatbot")

model_name = os.getenv("MODEL_NAME")
setup_env()

# ─── Session state defaults ───────────────────────────────────────────────────
def _init_state():
    defaults = {
        "session_id": str(uuid.uuid4()),
        "messages": [],
        "chatbot_ready": False,
        "vectorstore": None,
        "rag_chain": None,
        "history_store": {},
        "sources_loaded": [],
        "doc_count": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()

# ─── Core RAG builder ─────────────────────────────────────────────────────────
def get_embeddings():
    from langchain_huggingface import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def build_rag_chain(vectorstore):
    from langchain_groq import ChatGroq
    from langchain.chains.combine_documents import create_stuff_documents_chain
    from langchain.chains import create_retrieval_chain, create_history_aware_retriever
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

    chat_model = ChatGroq(model=model_name, temperature=0.7)
    retriever = vectorstore.as_retriever()

    # History-aware retriever
    ctx_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a query rewriter.

            Given a chat history and a follow-up question, convert the follow-up into a clear, standalone question.

            Guidelines:
            - Preserve all important details (names, dates, context, technical terms).
            - Resolve references like "it", "they", "this", etc. using the chat history.
            - Do NOT change the original intent of the question.
            - Keep the question concise and natural.
            - If the question is already standalone, return it unchanged.
            - Do NOT answer the question — only rewrite it.

            Output only the final standalone question."""),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
    history_retriever = create_history_aware_retriever(chat_model, retriever, ctx_prompt)

    # Answer chain
    answer_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful and precise assistant that answers questions using the provided context.

    <context>
    {context}
    </context>

    Rules:
    - Use ONLY the information present in the context to answer.
    - If the answer is not explicitly found in the context, say: "I don’t know based on the provided information."
    - Do NOT guess, assume, or add external knowledge.
    - Do NOT mention the word "context" in your response.
    - Keep answers clear, concise, and directly focused on the question.
    - If relevant, combine multiple pieces of information from the context, but do not repeat or quote unnecessarily.
    - Maintain factual accuracy above completeness.
    """),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    qa_chain = create_stuff_documents_chain(chat_model, answer_prompt)
    rag_chain = create_retrieval_chain(history_retriever, qa_chain)

    # Add session history
    from langchain_core.runnables.history import RunnableWithMessageHistory
    from langchain_community.chat_message_histories import ChatMessageHistory

    def get_history(sid: str):
        # Always read from the live session_state dict — never close over a local var
        store = st.session_state.setdefault("history_store", {})
        if sid not in store:
            store[sid] = ChatMessageHistory()
        return store[sid]

    return RunnableWithMessageHistory(
        rag_chain, get_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )

def store_documents(docs, vectorstore):
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents(docs)
    vectorstore.add_documents(chunks)
    return len(chunks)

def load_web_page(url: str):
    from langchain.schema import Document
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            text = soup.get_text(separator="\n", strip=True)
            return Document(page_content=text[:15000], metadata={"source": url})
        else:
            st.warning(f"⚠️ Could not load {url} (status {r.status_code})")
    except Exception as e:
        st.warning(f"⚠️ Error loading {url}: {e}")
    return None

_CHROMA_PATH = "./chroma_db"

def initialise_vectorstore():
    """Create a fresh persistent Chroma DB at a fixed temp path.
    Wiping the directory first avoids stale collection-ID mismatches."""
    import shutil
    from langchain_chroma import Chroma
    # Remove any leftover DB from a previous session so collection IDs stay clean
    if os.path.exists(_CHROMA_PATH):
        os.makedirs(_CHROMA_PATH, exist_ok=True)
    os.makedirs(_CHROMA_PATH, exist_ok=True)
    embeddings = get_embeddings()
    return Chroma(
        collection_name="rag_docs",
        embedding_function=embeddings,
        persist_directory=_CHROMA_PATH,
    )

# ─── Process sources ──────────────────────────────────────────────────────────
def process_sources(pdf_files, url_text: str):
    from langchain_community.document_loaders import PyMuPDFLoader
    all_docs = []
    source_labels = []

    # PDFs
    if pdf_files:
        for f in pdf_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(f.read())
                tmp_path = tmp.name
            loader = PyMuPDFLoader(tmp_path)
            docs = loader.load()
            for d in docs:
                d.metadata["source"] = f.name
            all_docs.extend(docs)
            source_labels.append(f"📄 {f.name}")
            os.unlink(tmp_path)

    # URLs
    if url_text.strip():
        urls = [u.strip() for u in url_text.split(",") if u.strip()]
        for url in urls:
            doc = load_web_page(url)
            if doc:
                all_docs.append(doc)
                source_labels.append(f"🌐 {url[:50]}…" if len(url) > 50 else f"🌐 {url}")

    return all_docs, source_labels

def clean_response(text: str) -> str:
    # remove <think>...</think>
    import re
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return text.strip()

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    # ───────────────── Header ─────────────────
    st.markdown("""
    <div style='text-align:center;padding:12px 0 18px;'>
        <div style='font-size:2.6rem;'>🧠</div>
        <div style='font-size:1.2rem;font-weight:700;color:#7dd3fc;letter-spacing:-0.5px;'>
            RAG Chatbot
        </div>
        <div style='font-size:0.75rem;color:#475569;'>
            PDFs + Web → Intelligent Q&A
        </div>
       <div style='font-size:0.75rem;color:red;'>
            Please do not apload any personal data
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ───────────────── Step 1: Upload ─────────────────
    st.markdown("### 📤 Step 1: Add Knowledge")

    pdf_files = st.file_uploader(
        "Upload PDFs",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload one or more PDF documents",
        label_visibility="collapsed",
    )

    if pdf_files:
        st.markdown("**Uploaded Files:**")
        for f in pdf_files:
            st.markdown(f"📄 `{f.name}`")

    url_input = st.text_area(
        "Website URLs",
        placeholder="https://example.com, https://docs.site.com",
        height=80,
        help="Comma-separated URLs",
    )

    st.markdown("---")

    # ───────────────── Step 2: Build ─────────────────
    st.markdown("### ⚙️ Step 2: Build Index")

    can_build = bool(pdf_files or url_input.strip())

    build_btn = st.button(
        "🚀 Build Chatbot",
        use_container_width=True,
        disabled=not can_build
    )

    if not can_build:
        st.caption("Upload PDFs or add URLs to enable building")

    if build_btn:
        with st.spinner("Processing documents..."):
            vs = initialise_vectorstore()
            docs, labels = process_sources(pdf_files, url_input)

            if docs:
                n = store_documents(docs, vs)

                st.session_state.vectorstore = vs
                st.session_state.rag_chain = build_rag_chain(vs)
                st.session_state.chatbot_ready = True
                st.session_state.sources_loaded = labels
                st.session_state.doc_count = n
                st.session_state.messages = []
                st.session_state.history_store = {}
                st.session_state.session_id = str(uuid.uuid4())

                st.success("Chatbot is ready!")
            else:
                st.error("No valid documents found")

    # ───────────────── Step 3: Status ─────────────────
    st.markdown("---")
    st.markdown("### 📊 Status")

    if st.session_state.chatbot_ready:
        st.markdown("""
        <div style='padding:10px 12px;background:rgba(16,185,129,0.1);
                    border:1px solid rgba(16,185,129,0.3);
                    border-radius:10px;color:#34d399;'>
            🟢 Ready to Chat
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='padding:10px 12px;background:rgba(251,191,36,0.1);
                    border:1px solid rgba(251,191,36,0.3);
                    border-radius:10px;color:#fbbf24;'>
            🟡 Waiting for Data
        </div>
        """, unsafe_allow_html=True)

    # ───────────────── Stats ─────────────────
    if st.session_state.chatbot_ready:
        st.markdown("### 📈 Session Stats")

        st.markdown(f"""
        <div class='info-card'>
            <div class='label'>Chunks Indexed</div>
            <div class='value'>{st.session_state.doc_count}</div>
        </div>

        <div class='info-card'>
            <div class='label'>Sources</div>
            <div class='value'>{len(st.session_state.sources_loaded)}</div>
        </div>
        """, unsafe_allow_html=True)

        # Sources list in cleaner format
        with st.expander("📚 View Sources", expanded=False):
            for s in st.session_state.sources_loaded:
                st.markdown(f"- {s}")

        st.markdown("---")

        if st.button("🔄 Reset Everything", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # ───────────────── Footer ─────────────────
    st.markdown("---")
    st.markdown("""
    <div style='text-align:center;font-size:0.7rem;color:#475569;'>
        LangChain • Groq • ChromaDB<br>
        RAG System v2.0
    </div>
    """, unsafe_allow_html=True)
# ─── Main content ─────────────────────────────────────────────────────────────
st.markdown("""
<div class='hero-header'>
  <div class='hero-title'>🧠 RAG Knowledge Chatbot</div>
  <div class='hero-sub'>Chat with your PDFs and websites using retrieval-augmented generation</div>
</div>
""", unsafe_allow_html=True)

# Status pill
if st.session_state.chatbot_ready:
    st.markdown("<div style='text-align:center'><div class='status-pill'>● Chatbot Ready</div></div>", unsafe_allow_html=True)
else:
    st.markdown("<div style='text-align:center'><div class='status-pill waiting'>⏳ Awaiting Sources</div></div>", unsafe_allow_html=True)

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ── Welcome / empty state ──
if not st.session_state.chatbot_ready and not st.session_state.messages:
    col1, col2, col3 = st.columns(3)
    cards = [
        ("📄", "Upload PDFs", "Drag & drop one or more PDF files in the sidebar"),
        ("🌐", "Add URLs", "Paste comma-separated website URLs to scrape"),
        ("💬", "Start Chatting", "Click 'Build Chatbot' and ask anything about your docs"),
    ]
    for col, (icon, title, desc) in zip([col1, col2, col3], cards):
        with col:
            st.markdown(f"""
            <div class='info-card' style='text-align:center;padding:24px 16px;'>
                <div style='font-size:2rem;margin-bottom:8px;'>{icon}</div>
                <div style='color:#7dd3fc;font-weight:600;font-size:1rem;margin-bottom:6px;'>{title}</div>
                <div style='color:#475569;font-size:0.82rem;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

# ── Render chat history ──
if st.session_state.messages:
    st.markdown("<div class='chat-wrapper'>", unsafe_allow_html=True)
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🧑" if msg["role"]=="user" else "🤖"):
            st.markdown(msg["content"])
    st.markdown("</div>", unsafe_allow_html=True)

# ── Chat input ──
if st.session_state.chatbot_ready:
    prompt = st.chat_input("Ask anything about your documents…")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking…"):
                response = st.session_state.rag_chain.invoke(
                    {"input": prompt},
                    config={"configurable": {"session_id": st.session_state.session_id}},
                )
                answer = response.get("answer", "I'm not sure about that.")
                answer = clean_response(answer)
            st.markdown(answer)
            # Show source metadata
            context_docs = response.get("context", [])
            if context_docs:
                unique_sources = list({d.metadata.get("source", "Unknown") for d in context_docs})
                chips = " ".join(f"<span class='source-chip'>📎 {s.split('/')[-1][:40]}</span>" for s in unique_sources)
                st.markdown(f"<div style='margin-top:8px;'>{chips}</div>", unsafe_allow_html=True)

        st.session_state.messages.append({"role": "assistant", "content": answer})
else:
    st.chat_input("Build the chatbot first using the sidebar →", disabled=True)