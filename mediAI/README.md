# MediAI — Multi-Agent Hospital System

A Streamlit + LangGraph multi-agent medical assistant with:
- **Receptionist Agent** — appointment booking with priority management
- **Reasoning Agent** — clinical triage and symptom analysis
- **Memory Agent** — permanent patient medical history
- **Clinical Summarizer** — doctor-facing patient summaries with RAG

---

## Project Structure

```
mediAI/
├── app.py                    # Streamlit entry point
├── agent_router.py           # Routes messages to correct agent
├── auth.py                   # Patient & doctor auth
├── database.py               # SQLAlchemy engine (PostgreSQL / SQLite)
├── db_helper.py              # Read-only dashboard queries
├── models.py                 # ORM models
├── summarizer_agent.py       # Clinical summarizer
├── structured_output.py      # Pydantic schemas
├── config.py                 # Env var loading
│
├── agents/
│   ├── memory_agent.py
│   ├── reasoning_agent.py
│   ├── receptionist_agent.py
│   └── prompts/
│       ├── memory_prompt.py
│       ├── reasoning_prompt.py
│       └── receptionist_prompt.py
│
├── tools/
│   ├── appointment_tool.py
│   ├── clinical_triage_tool.py
│   ├── doctor_tool.py
│   ├── email_tool.py
│   └── memory_tool.py
│
├── rag/
│   ├── chroma_db.py
│   ├── ingest.py
│   └── retriever.py
│
├── memory_store/
│   └── permanent_memory.py
│
├── requirements.txt
├── Procfile
├── railway.toml
└── .env.example
```

---

## Deploy to Railway (Step-by-Step)

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/YOUR_USERNAME/mediAI.git
git push -u origin main
```

> Since your GitHub account is flagged, you can push to a **new repository** 
> created under a different account, or push directly via Railway CLI (see Step 5).

---

### 2. Create Railway Project

1. Go to [railway.app](https://railway.app) → **New Project**
2. Choose **Deploy from GitHub repo** → select your repo
3. Railway will auto-detect the `Procfile` and `requirements.txt`

---

### 3. Add PostgreSQL Plugin

1. In your Railway project dashboard → **+ New** → **Database** → **PostgreSQL**
2. Railway will automatically inject `DATABASE_URL` into your service environment
3. No code changes needed — `database.py` reads it automatically

---

### 4. Set Environment Variables

In Railway dashboard → your service → **Variables** tab, add:

| Variable | Value |
|---|---|
| `GROQ_API_KEY` | Your Groq API key |
| `EMAIL_ADDRESS` | Your Gmail address |
| `EMAIL_PASSWORD` | Your Gmail **App Password** (not your login password) |

> `DATABASE_URL` is injected automatically by the PostgreSQL plugin — do NOT set it manually.

---

### 5. Alternative: Deploy via Railway CLI (no GitHub needed)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Init project in your project folder
cd mediAI
railway init

# Add PostgreSQL
railway add --plugin postgresql

# Set env vars
railway variables set GROQ_API_KEY=your_key
railway variables set EMAIL_ADDRESS=your_email
railway variables set EMAIL_PASSWORD=your_app_password

# Deploy
railway up
```

---

### 6. ChromaDB Persistence (Optional but Recommended)

By default ChromaDB writes to `/tmp/chroma_db` which resets on Railway redeploys.

To persist it:
1. Railway dashboard → your service → **Volumes** → **Add Volume**
2. Mount path: `/data`
3. Add env var: `CHROMA_PATH=/data/chroma_db`

---

### 7. Gmail App Password Setup

Gmail blocks plain password login. Use an App Password:
1. Google Account → Security → 2-Step Verification (enable it)
2. Security → App Passwords → create one for "Mail"
3. Use that 16-character password as `EMAIL_PASSWORD`

---

## Local Development

```bash
# Clone and install
pip install -r requirements.txt

# Create .env from example
cp .env.example .env
# Fill in your values

# Run
streamlit run app.py
```
