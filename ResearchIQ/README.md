# ResearchIQ
## AI-Powered Research Paper Analysis, Quality Assessment & Publication Readiness Platform

ResearchIQ is a production-grade full-stack web application designed for students, research scholars, faculty, and academic authors to rigorously evaluate research manuscripts prior to journal or conference submission.

---

## 🚀 Key Features

The platform implements 10 core analytical modules:

1. **Automated Technical Review**: Section-by-section evaluation (Abstract, Methodology, Results, Discussion, Conclusion) for completeness, logical cohesion, and experimental rigor.
2. **Novelty Analysis**: Real-time scholarly discovery using the OpenAlex API & sentence-transformer embeddings to detect thematic overlap and unaddressed research gaps.
3. **Citation & Bibliographic Analysis**: Cross-referencing between in-text citations and reference entries (IEEE, APA, MLA), flagging orphaned citations, duplicates, and missing years.
4. **Academic Writing Quality**: Grammar analysis, passive voice overuse detection, wordiness elimination, and academic tone scoring.
5. **Plagiarism Risk Detection**: TF-IDF cosine similarity, n-gram fingerprinting, and paragraph duplication checks against indexed academic literature.
6. **Figure & Table Validation**: Detects sequence numbering skips, duplicate numbers, unreferenced visual assets, and low-resolution graphics (<300 DPI).
7. **AI Peer Reviewer Critique**: Objective peer-review feedback powered by Google Gemini API (with a grounded rule-based fallback).
8. **Journal & Conference Matching**: Authentic venue discovery powered by OpenAlex registry with real publisher names and verified ISSNs (zero fabricated impact factors).
9. **Patentability Indicator**: Preliminary assessment of industrial applicability, technical enablement, and statutory subject matter eligibility.
10. **Publication Readiness Score**: Dynamic, weighted multi-attribute score categorizing submissions into *Ready for Submission*, *Minor Revision*, or *Major Revision*.

---

## 🛠️ Technology Stack

- **Frontend**: Next.js 14+ (App Router), React, TypeScript, Tailwind CSS, Lucide React, Recharts, Axios, React Hook Form, Zod.
- **Backend**: Python 3.12+, FastAPI, SQLAlchemy, PostgreSQL, PyMuPDF, python-docx, ReportLab (PDF Reports), Scikit-learn, Sentence-Transformers, Google Gemini API.
- **Database**: PostgreSQL 16.
- **Containerization**: Docker & Docker Compose.

---

## 📁 Directory Structure

```text
ResearchIQ/
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx               # Landing Page
│   │   │   ├── login/page.tsx         # User Login
│   │   │   ├── register/page.tsx      # User Registration
│   │   │   ├── dashboard/page.tsx     # Author KPI Dashboard
│   │   │   ├── upload/page.tsx        # Drag & Drop Manuscript Upload
│   │   │   ├── analysis/page.tsx      # 10-Feature Multi-Tab Evaluation
│   │   │   └── history/page.tsx       # Evaluation Archive
│   │   ├── components/layout/         # Navbar, Footer
│   │   ├── services/api.ts            # Central Axios API Service
│   │   ├── types/index.ts             # TypeScript Type Definitions
│   │   └── styles/globals.css
│   ├── package.json
│   ├── tsconfig.json
│   └── Dockerfile
│
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI Entrypoint
│   │   ├── core/                      # Config & Security
│   │   ├── database/                  # SQLAlchemy Session & Engine
│   │   ├── models/                    # User, Paper, Analysis Models
│   │   ├── schemas/                   # Pydantic Request/Response Models
│   │   ├── routers/                   # Auth, Papers, Analysis Routers
│   │   ├── services/                  # Analysis Coordinator & PDF Report Generator
│   │   ├── paper_processing/          # PyMuPDF & python-docx Extractor
│   │   ├── ai_engine/                 # 10 Dedicated Analytical Modules
│   │   └── tests/                     # Pytest Unit & Integration Tests
│   ├── uploads/                       # Isolated storage sandbox
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
│
├── docker-compose.yml
└── README.md
```

---

## ⚡ Quick Start with Docker Compose

To start the entire platform (PostgreSQL, FastAPI Backend, and Next.js Frontend) in a single command:

```bash
docker-compose up -d
```

- **Frontend UI**: [http://localhost:3001](http://localhost:3001)
- **Backend API & Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **PostgreSQL**: `localhost:5432` (User: `researchiq`, DB: `researchiq_db`)

---

## 💻 Manual Local Development

### 1. Backend Setup (FastAPI)

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate   # On Windows
# source venv/bin/activate # On Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
copy .env.example .env

# Run FastAPI development server
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup (Next.js)

```bash
cd frontend

# Install npm packages
npm install

# Run Next.js development server on port 3001
npm run dev
```

Visit [http://localhost:3001](http://localhost:3001) in your browser.

---

## 🧪 Running Unit & Integration Tests

Run the test suite inside the `backend` directory:

```bash
cd backend
pytest app/tests/ -v
```

---

## 🔒 Security & Scholarly Integrity

- **Password Hashing**: Uses `passlib[bcrypt]` with salted hashing.
- **JWT Authentication**: Short-lived cryptographic tokens for protected routes.
- **Zero Fabrication Policy**: ResearchIQ never fabricates impact factors, rankings, or citations. All recommendations derive from active scholarly registries (OpenAlex/Crossref).
