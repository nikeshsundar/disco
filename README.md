# CYGNUSA Elite-Hire: AI-Enabled HR Evaluation System

A full-stack HR evaluation system built for the SRM Innovation Hackathon. This system manages the complete hiring journey from resume upload to final hiring decision with transparent rationale.

## 🌟 Features

### 1. Multi-Modal Assessment Engine
- **Scenario-based MCQs**: Workplace situations with best response options
- **Coding Sandbox**: Functional IDE with code execution and test cases
- **Text Responses**: Open-ended questions for communication evaluation
- **Slider Inputs**: Psychometric assessments with preference scales

### 2. Dual-Track Assessment
- **Technical Assessment**: Syntax, logic, system design, and domain knowledge
- **Psychometric Assessment**: Emotional intelligence, resilience, leadership, and culture fit

### 3. Integrity Shield (Proctoring)
- **Visual Monitoring**: Webcam face detection
- **Environmental Control**: Tab-switching, copy-paste, and keyboard shortcut detection
- **Audit Trail**: Complete logging of suspicious events with timestamps

### 4. Smart Resume Shortlisting
- **Parsing Logic**: Extract skills, experience, and education from PDFs/DOCX
- **Scoring Heuristics**: Match against job descriptions
- **Auto-Ranking**: Candidates sorted into "High Match", "Potential", and "Reject"

### 5. Explainable AI Decision Engine
- **Automated Decision**: Final "Hire/No-Hire" recommendation
- **Rationale Generation**: Text-based justification for every decision
- **Competency Mapping**: Visual breakdown of strengths vs. weaknesses

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: SQLite (dev) / PostgreSQL (production)
- **ORM**: SQLAlchemy
- **Authentication**: JWT with bcrypt

### Frontend
- **Framework**: Next.js 14 (React)
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Code Editor**: Monaco Editor
- **Webcam**: react-webcam

## 📦 Quick Start (Windows)

### Prerequisites
- Python 3.9+
- Node.js 18+

### Step 1: Backend Setup

Open a terminal and run:

```powershell
cd e:\hackthon\backend
pip install -r requirements.txt
python seed_data.py
python run_server.py
```

### Step 2: Frontend Setup

Open a **second terminal** and run:

```powershell
cd e:\hackthon\frontend
npm install
npm run dev
```

### Step 3: Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Test Credentials
- **Recruiter**: recruiter@cygnusa.com / password123

### Workflow

#### For Candidates:
1. Register as a candidate
2. Upload your resume (PDF/DOCX)
3. Browse available job positions
4. Start an assessment
5. Complete MCQs, coding challenges, and psychometric questions
6. View your evaluation and recommendation

#### For Recruiters:
1. Login as recruiter
2. Create job postings with required skills
3. View candidate applications
4. Review detailed evaluations with rationale
5. Use shortlist feature to filter candidates

## 📊 Scoring Algorithm

### Resume Match (25%)
- Required skills match: 50%
- Preferred skills match: 15%
- Experience match: 20%
- Education match: 15%

### Assessment Score (55%)
- Technical questions: 60%
- Psychometric questions: 40%

### Integrity Score (20%)
- Based on proctoring events
- Deductions for violations

### Final Decision
- **HIRE**: Score ≥ 75% AND Integrity ≥ 70%
- **CONSIDER**: Score ≥ 50% AND Integrity ≥ 50%
- **NO HIRE**: Below thresholds

## 📁 Project Structure

```
hackthon/
├── backend/
│   ├── app/
│   │   ├── api/           # API route handlers
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   ├── config.py      # Configuration
│   │   ├── database.py    # Database setup
│   │   └── main.py        # FastAPI app
│   ├── uploads/           # Resume storage
│   ├── requirements.txt
│   ├── seed_data.py       # Sample data
│   └── .env
│
└── frontend/
    ├── src/
    │   ├── app/           # Next.js pages
    │   │   ├── candidate/ # Candidate pages
    │   │   ├── recruiter/ # Recruiter pages
    │   │   ├── login/
    │   │   └── register/
    │   └── lib/           # Utilities
    │       ├── api.ts     # API client
    │       └── store.ts   # State management
    ├── package.json
    └── .env.local
```

## 🔒 Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Protected API routes
- Sandboxed code execution
- CORS configuration

## 🎯 Evaluation Criteria Alignment

| Criteria | Weight | Implementation |
|----------|--------|----------------|
| Architectural Depth | 30% | Modular microservice-ready architecture with clean separation |
| Grading Accuracy | 20% | Rule-based scoring with transparent algorithms |
| Logic Transparency | 20% | Explainable rationale for every decision |
| Security & Anti-Cheat | 15% | Proctoring system with audit trail |
| User Experience | 15% | Clean, intuitive UI with real-time feedback |

## 👥 Team

SRM Innovation Hackathon - Edition 1

## 📄 License

MIT License - Built for educational purposes
