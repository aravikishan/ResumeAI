# ResumeAI

![Python](https://img.shields.io/badge/Python-3.10%2B-3776ab?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask)
![License](https://img.shields.io/badge/License-MIT-green)
![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen)
![Coverage](https://img.shields.io/badge/Coverage-92%25-brightgreen)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![CI](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?logo=githubactions&logoColor=white)

**AI-powered resume parser** with skill extraction, ATS compatibility scoring, experience level detection, improvement suggestions, and job matching -- all using rule-based analysis (no external AI/LLM APIs required).

---

## Features

- **Resume Parsing** -- Extract name, email, phone, skills, experience, and education from plain text
- **Section Extraction** -- Detect Contact, Summary, Experience, Education, Skills, Certifications, Projects, and more
- **Skill Extraction** -- Match against 150+ skills across 6 categories using keyword matching
- **ATS Scoring** -- 0-100 compatibility score with detailed breakdown across 7 criteria
- **Experience Level Detection** -- Automatic classification as Entry / Mid / Senior / Lead
- **Improvement Suggestions** -- Actionable recommendations to strengthen your resume
- **Job Matching** -- Compare resume skills against job requirements with match percentage
- **Match All Jobs** -- Simultaneously match against all available positions, sorted by fit
- **Analysis History** -- Track all parsed resumes in a local SQLite database
- **File Upload** -- Drag-and-drop .txt file upload with progress visualization
- **Professional UI** -- Clean, responsive blue/white interface with animated score charts
- **REST API** -- Full JSON API for programmatic access

## Screenshots

| Upload & Parse | ATS Score | Job Matching |
|:-:|:-:|:-:|
| Paste or drag-drop resume | Animated score breakdown | Skill gap analysis |

## Tech Stack

| Component   | Technology         | Version |
|-------------|--------------------|---------|
| Backend     | Flask              | 3.0.0   |
| Database    | SQLite + SQLAlchemy| 2.0.23  |
| ORM Models  | SQLAlchemy         | 2.0.23  |
| Validation  | Pydantic           | 2.5.2   |
| Testing     | pytest + coverage  | 7.4.3   |
| Linting     | flake8             | 6.1.0   |
| Container   | Docker + Compose   | 3.8     |
| CI/CD       | GitHub Actions     | v4      |
| Production  | Gunicorn           | 21.2.0  |

## Quick Start

### Local Development

```bash
# Clone the repository
git clone https://github.com/ravikishan/ResumeAI.git
cd ResumeAI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

Open **http://localhost:8005** in your browser.

### Using start.sh

```bash
chmod +x start.sh
./start.sh
```

### Docker

```bash
# Build and run
docker-compose up --build

# Or manually
docker build -t resumeai .
docker run -p 8005:8005 resumeai
```

## API Endpoints

| Method | Endpoint              | Description                        |
|--------|-----------------------|------------------------------------|
| GET    | `/api/health`         | Health check                       |
| POST   | `/api/parse`          | Parse resume text (full analysis)  |
| POST   | `/api/ats-score`      | Get ATS compatibility score only   |
| POST   | `/api/match`          | Match resume against a specific job|
| POST   | `/api/match-all`      | Match resume against all jobs      |
| GET    | `/api/resumes`        | List recently parsed resumes       |
| GET    | `/api/resumes/:id`    | Get a specific resume analysis     |
| GET    | `/api/jobs`           | List available job postings        |
| GET    | `/api/sample`         | Get sample resume text             |
| GET    | `/api/skills/categories` | List skill categories and counts |

### Parse a Resume

```bash
curl -X POST http://localhost:8005/api/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "John Doe\nSoftware Engineer\nEmail: john@example.com\n5 years of experience\nSkills: Python, Flask, AWS, Docker\nBachelor of Science in CS\nLeadership, Communication"}'
```

**Response:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": null,
  "sections": {},
  "skills": {
    "Programming": ["Python"],
    "Frameworks": ["Flask"],
    "Cloud": ["AWS", "Docker"]
  },
  "experience_years": 5.0,
  "experience_level": "Mid",
  "education": "Bachelor of Science",
  "ats_score": 62,
  "ats_breakdown": {
    "contact_email": 10,
    "contact_phone": 0,
    "skills_count": 8,
    "skill_diversity": 9,
    "education": 10,
    "experience": 15,
    "formatting": 10
  },
  "suggestions": [
    "Include a phone number for direct communication with hiring managers.",
    "Add a professional summary or objective at the top of your resume."
  ]
}
```

### ATS Score

```bash
curl -X POST http://localhost:8005/api/ats-score \
  -H "Content-Type: application/json" \
  -d '{"text": "resume text here..."}'
```

### Job Matching

```bash
curl -X POST http://localhost:8005/api/match \
  -H "Content-Type: application/json" \
  -d '{"resume_text": "...", "job_id": 1}'
```

### Match All Jobs

```bash
curl -X POST http://localhost:8005/api/match-all \
  -H "Content-Type: application/json" \
  -d '{"resume_text": "..."}'
```

## Skill Categories

ResumeAI recognizes skills across **6 categories** with **150+ skills**:

| Category       | Count | Examples                                          |
|----------------|-------|---------------------------------------------------|
| Programming    | 30    | Python, Java, JavaScript, C++, Go, Rust, SQL      |
| Frameworks     | 30    | React, Angular, Vue.js, Flask, Django, Node.js     |
| Cloud          | 30    | AWS, Azure, GCP, Docker, Kubernetes, Terraform     |
| Data           | 30    | Pandas, NumPy, TensorFlow, PyTorch, Spark          |
| Databases      | 19    | PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch   |
| Soft Skills    | 20    | Leadership, Communication, Problem-solving         |

## ATS Scoring Criteria

| Criterion           | Max Points | Description                              |
|----------------------|-----------|------------------------------------------|
| Email present        | 10        | Professional email address detected       |
| Phone present        | 10        | Phone number detected                     |
| Skills listed        | 20        | Number of recognized skills (2 pts each)  |
| Skill diversity      | 15        | Skills across categories (3 pts each)     |
| Education            | 15        | Degree level (Bachelor=10, Master/PhD=15) |
| Experience           | 15        | Years mentioned (2+=5, 5+=15)             |
| Formatting & quality | 15        | Name, sections, action verbs, length      |
| **Total**            | **100**   |                                           |

## Experience Level Detection

| Level   | Years       |
|---------|-------------|
| Entry   | 0 -- 2      |
| Mid     | 3 -- 5      |
| Senior  | 6 -- 10     |
| Lead    | 11+         |

## Architecture

```
ResumeAI/
├── app.py                 # Flask application factory
├── config.py              # Configuration class
├── models/
│   ├── database.py        # SQLAlchemy setup
│   └── schemas.py         # Resume, Skill, JobMatch models + Pydantic schemas
├── services/
│   ├── parser.py          # Section extraction, skill matching, suggestions
│   └── scorer.py          # ATS scoring, job matching engine
├── routes/
│   ├── api.py             # JSON API endpoints
│   └── views.py           # HTML view routes
├── templates/             # Jinja2 templates (6 pages)
├── static/
│   ├── css/style.css      # Professional blue/white theme
│   └── js/main.js         # Drag-drop, progress, charts, interactivity
├── tests/                 # 40+ pytest tests
├── seed_data/             # Sample resumes and job descriptions
├── Dockerfile             # Production container
├── docker-compose.yml     # Container orchestration
└── .github/workflows/     # CI pipeline (lint + test)
```

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# With coverage report
python -m pytest tests/ -v --cov=. --cov-report=term-missing

# Run specific test file
python -m pytest tests/test_services.py -v
```

## Development

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run with debug mode
FLASK_DEBUG=1 python app.py

# Lint
flake8 . --max-line-length=120

# Verify syntax
python -c "import ast; [ast.parse(open(f).read()) for f in __import__('glob').glob('**/*.py', recursive=True)]"
```

## Environment Variables

| Variable      | Default                   | Description            |
|---------------|---------------------------|------------------------|
| `PORT`        | `8005`                  | Server port            |
| `SECRET_KEY`  | `resumeai-secret-key...`  | Flask secret key       |
| `DATABASE_URL`| `sqlite:///instance/...`  | Database connection    |
| `FLASK_DEBUG` | `0`                       | Debug mode (0 or 1)    |

## License

MIT License -- see [LICENSE](LICENSE) for details.

---

Built with Python and Flask | [ravikishan](https://github.com/ravikishan)
