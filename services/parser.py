"""Resume text parsing and section extraction.

All analysis is rule-based -- no external AI/LLM calls.
Uses regex patterns to extract contact info, sections, skills,
experience, and education from plain-text resumes.
"""

import re
from typing import Optional


# ── Comprehensive Skill Database ─────────────────────────────────────────

SKILL_DATABASE: dict[str, list[str]] = {
    "Programming": [
        "Python", "Java", "JavaScript", "C++", "C#", "Go", "Rust",
        "TypeScript", "Ruby", "PHP", "Swift", "Kotlin", "SQL", "R",
        "Scala", "Perl", "Haskell", "Lua", "Dart", "MATLAB",
        "Objective-C", "Shell", "Bash", "PowerShell", "Elixir",
        "Clojure", "F#", "Groovy", "Julia", "COBOL",
    ],
    "Frameworks": [
        "React", "Angular", "Vue.js", "Node.js", "Django", "Flask",
        "FastAPI", "Spring Boot", "Express.js", "Next.js", "Nuxt.js",
        "Svelte", "jQuery", "Bootstrap", "Tailwind CSS", "HTML",
        "CSS", "SASS", "GraphQL", "REST API", "WebSocket",
        "Ruby on Rails", "Laravel", "ASP.NET", "Gin", "Echo",
        "Actix", "Rocket", "Gatsby", "Remix", "SvelteKit",
    ],
    "Databases": [
        "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch",
        "DynamoDB", "Cassandra", "SQLite", "Oracle", "SQL Server",
        "Firebase", "Neo4j", "CouchDB", "MariaDB", "InfluxDB",
        "Supabase", "PlanetScale", "CockroachDB", "Memcached",
    ],
    "Cloud": [
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform",
        "CI/CD", "Jenkins", "GitHub Actions", "GitLab CI",
        "Ansible", "CloudFormation", "Heroku", "DigitalOcean",
        "Nginx", "Apache", "Linux", "Serverless", "Lambda",
        "Cloud Run", "ECS", "EKS", "Vercel", "Netlify",
        "Pulumi", "Vagrant", "Prometheus", "Grafana", "Datadog",
    ],
    "Data": [
        "Pandas", "NumPy", "TensorFlow", "PyTorch", "Spark",
        "Hadoop", "Tableau", "Power BI", "Scikit-learn", "Keras",
        "OpenCV", "NLTK", "spaCy", "Matplotlib", "Seaborn",
        "Jupyter", "Airflow", "dbt", "Looker", "Data Pipeline",
        "Kafka", "RabbitMQ", "Celery", "MLflow", "Kubeflow",
        "Ray", "Dask", "Polars", "Apache Beam", "Flink",
    ],
    "Soft Skills": [
        "Leadership", "Communication", "Problem-solving",
        "Teamwork", "Project Management", "Agile", "Scrum",
        "Mentoring", "Presentation", "Critical Thinking",
        "Time Management", "Collaboration", "Adaptability",
        "Creativity", "Negotiation", "Stakeholder Management",
        "Strategic Planning", "Decision Making", "Coaching",
        "Conflict Resolution",
    ],
}

# Headings that indicate resume sections
SECTION_HEADINGS = {
    "contact": ["contact", "contact information", "personal information",
                 "personal details"],
    "summary": ["summary", "objective", "professional summary",
                 "career objective", "profile", "about me", "about",
                 "career summary", "executive summary"],
    "experience": ["experience", "work experience", "professional experience",
                    "employment history", "work history", "career history",
                    "employment"],
    "education": ["education", "academic background", "academic history",
                   "qualifications", "academic qualifications"],
    "skills": ["skills", "technical skills", "core competencies",
               "competencies", "areas of expertise", "expertise",
               "technologies", "tech stack"],
    "certifications": ["certifications", "certificates", "professional certifications",
                        "licenses", "credentials", "accreditations"],
    "projects": ["projects", "key projects", "notable projects",
                  "personal projects", "side projects"],
    "awards": ["awards", "honors", "achievements", "recognition",
               "accomplishments"],
    "publications": ["publications", "papers", "research"],
    "references": ["references"],
}

# Action verbs used in strong resumes
ACTION_VERBS = {
    "led", "managed", "developed", "designed", "implemented", "built",
    "created", "delivered", "launched", "increased", "improved",
    "reduced", "optimized", "architected", "automated", "deployed",
    "established", "mentored", "coordinated", "collaborated",
    "analyzed", "resolved", "streamlined", "spearheaded",
    "negotiated", "orchestrated", "pioneered", "transformed",
    "accelerated", "achieved", "administered", "consolidated",
    "directed", "engineered", "executed", "facilitated",
    "generated", "initiated", "integrated", "maintained",
    "modernized", "overhauled", "restructured", "revamped",
    "supervised", "trained", "upgraded",
}


def parse_resume(text: str) -> dict:
    """Parse resume text and return comprehensive structured data.

    Returns a dict with name, email, phone, sections, skills (by category),
    experience_years, experience_level, education, ats_score,
    ats_breakdown, and suggestions.
    """
    sections = extract_sections(text)
    name = extract_name(text)
    email = extract_email(text)
    phone = extract_phone(text)
    skills = extract_skills(text)
    experience = extract_experience(text)
    education = extract_education(text)
    experience_level = detect_experience_level(experience)

    parsed: dict = {
        "name": name,
        "email": email,
        "phone": phone,
        "sections": sections,
        "skills": skills,
        "experience_years": experience,
        "experience_level": experience_level,
        "education": education,
    }

    return parsed


def extract_sections(text: str) -> dict[str, str]:
    """Extract resume sections using heading detection.

    Returns a dict mapping section names (contact, summary, experience,
    education, skills, certifications) to their raw text content.
    """
    lines = text.strip().splitlines()
    found_sections: dict[str, str] = {}
    current_section: Optional[str] = None
    current_lines: list[str] = []

    # Build a reverse mapping: lowercase heading -> section key
    heading_map: dict[str, str] = {}
    for section_key, headings in SECTION_HEADINGS.items():
        for h in headings:
            heading_map[h] = section_key

    for line in lines:
        stripped = line.strip()
        stripped_lower = stripped.lower().rstrip(":")

        if stripped_lower in heading_map:
            # Save previous section
            if current_section and current_lines:
                content = "\n".join(current_lines).strip()
                if content:
                    found_sections[current_section] = content
            current_section = heading_map[stripped_lower]
            current_lines = []
        elif current_section is not None:
            current_lines.append(line)

    # Save last section
    if current_section and current_lines:
        content = "\n".join(current_lines).strip()
        if content:
            found_sections[current_section] = content

    return found_sections


def extract_email(text: str) -> Optional[str]:
    """Extract the first email address found in the text."""
    pattern = r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
    match = re.search(pattern, text)
    return match.group(0) if match else None


def extract_phone(text: str) -> Optional[str]:
    """Extract the first phone number found in the text."""
    patterns = [
        r"\+?1?[\s.-]?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}",
        r"\+?\d{1,3}[\s.-]?\d{3,5}[\s.-]?\d{4,6}",
        r"\(\d{3}\)\s*\d{3}[\s.-]?\d{4}",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0).strip()
    return None


def extract_name(text: str) -> Optional[str]:
    """Extract the candidate name using heuristics.

    Strategy: take the first non-empty line that looks like a name
    (starts with a capital letter, contains only letters and spaces,
    2-5 words, and is not a common heading).
    """
    headings = set()
    for heading_list in SECTION_HEADINGS.values():
        headings.update(heading_list)

    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.lower().rstrip(":") in headings:
            continue
        # Name-like: starts with uppercase, mostly letters/spaces
        if re.match(r"^[A-Z][a-zA-Z.\-\']+(?:\s+[A-Z][a-zA-Z.\-\']*)+$", line):
            words = line.split()
            if 2 <= len(words) <= 5:
                return line
        # Fallback: first line with 2-4 title-case words
        words = line.split()
        if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w):
            if not any(kw in line.lower() for kw in headings):
                return line
    return None


def extract_skills(text: str) -> dict[str, list[str]]:
    """Match resume text against the comprehensive skill dictionary.

    Returns a dict mapping category names to lists of matched skills.
    Case-insensitive matching with word boundary detection.
    """
    found: dict[str, list[str]] = {}
    text_lower = text.lower()
    for category, skills in SKILL_DATABASE.items():
        matched = []
        for skill in skills:
            escaped = re.escape(skill)
            pattern = rf"\b{escaped}\b"
            if re.search(pattern, text_lower, re.IGNORECASE):
                matched.append(skill)
        if matched:
            found[category] = sorted(matched)
    return found


def extract_experience(text: str) -> Optional[float]:
    """Extract years of experience mentioned in the resume.

    Searches for common patterns like "X years of experience",
    "X+ years in", etc. Returns the highest number found.
    """
    patterns = [
        r"(\d+\.?\d*)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience",
        r"experience\s*:?\s*(\d+\.?\d*)\+?\s*(?:years?|yrs?)",
        r"(\d+\.?\d*)\+?\s*(?:years?|yrs?)\s+(?:in|of|working)",
        r"over\s+(\d+\.?\d*)\s*(?:years?|yrs?)",
        r"(\d+\.?\d*)\s*(?:years?|yrs?)\s+(?:professional|industry)",
    ]
    max_years = None
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            try:
                years = float(m)
                if years > 50:
                    continue  # Skip unreasonable values
                if max_years is None or years > max_years:
                    max_years = years
            except ValueError:
                continue
    return max_years


def extract_education(text: str) -> Optional[str]:
    """Extract highest education level found in the resume."""
    degree_patterns = [
        (r"\b(?:Ph\.?D|Doctorate|Doctor of Philosophy)\b", "PhD"),
        (r"\b(?:M\.?S\.?|M\.?Sc|Master(?:s|\'s)?\s+(?:of|in)\s+Science)\b", "Master of Science"),
        (r"\b(?:M\.?B\.?A|Master(?:s|\'s)?\s+(?:of|in)\s+Business)\b", "MBA"),
        (r"\b(?:M\.?A\.?|Master(?:s|\'s)?\s+(?:of|in)\s+Arts?)\b", "Master of Arts"),
        (r"\bMaster(?:s|\'s)?\s+(?:Degree|of|in)\b", "Master\'s Degree"),
        (r"\b(?:B\.?S\.?|B\.?Sc|Bachelor(?:s|\'s)?\s+(?:of|in)\s+Science)\b", "Bachelor of Science"),
        (r"\b(?:B\.?A\.?|Bachelor(?:s|\'s)?\s+(?:of|in)\s+Arts?)\b", "Bachelor of Arts"),
        (r"\bBachelor(?:s|\'s)?\s+(?:Degree|of|in)\b", "Bachelor\'s Degree"),
        (r"\b(?:Associate(?:s|\'s)?\s+Degree)\b", "Associate\'s Degree"),
        (r"\b(?:High School Diploma|GED)\b", "High School"),
    ]
    for pattern, label in degree_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return label
    return None


def detect_experience_level(years: Optional[float]) -> str:
    """Determine experience level from years of experience.

    Returns one of: Entry, Mid, Senior, Lead, or Unknown.
    """
    if years is None:
        return "Unknown"
    if years <= 2:
        return "Entry"
    elif years <= 5:
        return "Mid"
    elif years <= 10:
        return "Senior"
    else:
        return "Lead"


def count_action_verbs(text: str) -> int:
    """Count how many strong action verbs appear in the resume."""
    text_lower = text.lower()
    count = 0
    for verb in ACTION_VERBS:
        pattern = rf"\b{re.escape(verb)}\b"
        if re.search(pattern, text_lower):
            count += 1
    return count


def get_improvement_suggestions(parsed: dict) -> list[str]:
    """Generate actionable improvement suggestions based on the parsed data.

    Examines completeness of contact info, skills, sections, and
    formatting to produce targeted recommendations.
    """
    suggestions: list[str] = []

    # Contact information
    if not parsed.get("email"):
        suggestions.append(
            "Add a professional email address to ensure recruiters can contact you."
        )
    if not parsed.get("phone"):
        suggestions.append(
            "Include a phone number for direct communication with hiring managers."
        )
    if not parsed.get("name"):
        suggestions.append(
            "Make sure your full name appears prominently at the top of your resume."
        )

    # Skills
    skills = parsed.get("skills", {})
    total_skills = sum(len(v) for v in skills.values())
    categories_with_skills = len(skills)

    if total_skills < 5:
        suggestions.append(
            "List more technical skills -- aim for at least 8-10 relevant skills "
            "to pass ATS keyword filters."
        )
    if categories_with_skills < 3:
        suggestions.append(
            "Diversify your skills across more categories (e.g., add cloud, "
            "database, or framework skills alongside programming languages)."
        )
    if "Soft Skills" not in skills:
        suggestions.append(
            "Add soft skills like Leadership, Communication, or Teamwork -- "
            "many employers value these alongside technical abilities."
        )

    # Education
    if not parsed.get("education"):
        suggestions.append(
            "Include your educational background with degree type and institution name."
        )

    # Experience
    if not parsed.get("experience_years"):
        suggestions.append(
            "Quantify your experience -- mention total years of experience explicitly "
            "(e.g., '5 years of experience in software development')."
        )

    # Sections
    sections = parsed.get("sections", {})
    if "summary" not in sections:
        suggestions.append(
            "Add a professional summary or objective at the top of your resume "
            "to give recruiters a quick overview of your qualifications."
        )
    if "experience" not in sections:
        suggestions.append(
            "Include a clearly labeled Experience or Work History section "
            "with job titles, companies, and dates."
        )
    if "certifications" not in sections:
        suggestions.append(
            "Consider adding relevant certifications to strengthen your profile "
            "(e.g., AWS, PMP, or industry-specific credentials)."
        )

    # General formatting
    if total_skills >= 5 and parsed.get("education") and parsed.get("experience_years"):
        if len(suggestions) == 0:
            suggestions.append(
                "Your resume looks comprehensive! Consider tailoring it to each "
                "specific job posting for the best results."
            )

    return suggestions


def get_sample_resume() -> str:
    """Return a realistic sample resume as plain text."""
    return """John Anderson
Senior Software Engineer

Contact
Email: john.anderson@email.com
Phone: (555) 123-4567
Location: San Francisco, CA
LinkedIn: linkedin.com/in/johnanderson

Summary
Innovative software engineer with 8 years of experience building scalable
web applications and distributed systems. Passionate about clean code,
test-driven development, and mentoring junior developers. Proven track
record of delivering high-impact projects on time.

Experience
Senior Software Engineer | TechCorp Inc. | 2020 - Present
- Led development of microservices architecture serving 2M+ users
- Built real-time data pipeline using Python, Spark, and Kafka
- Implemented CI/CD pipelines with Jenkins and GitHub Actions
- Mentored team of 5 junior developers
- Reduced deployment time by 60% through automation

Software Engineer | DataFlow Systems | 2017 - 2020
- Developed REST APIs using Flask and FastAPI
- Managed PostgreSQL and Redis databases
- Deployed applications on AWS using Docker and Kubernetes
- Improved API response time by 40% through query optimization
- Collaborated with product team on feature specifications

Junior Developer | WebStart LLC | 2015 - 2017
- Built responsive web applications using React and JavaScript
- Collaborated with design team on UI/UX improvements
- Wrote unit and integration tests with pytest
- Participated in Agile sprint planning and retrospectives

Education
Master of Science in Computer Science
Stanford University | 2015

Bachelor of Science in Computer Science
UC Berkeley | 2013

Skills
Programming: Python, Java, JavaScript, TypeScript, SQL, Go
Frameworks: React, Flask, FastAPI, Node.js, REST API, HTML, CSS
Cloud: AWS, Docker, Kubernetes, Jenkins, CI/CD, GitHub Actions, Linux
Data: Pandas, NumPy, Spark, TensorFlow, Kafka
Databases: PostgreSQL, Redis, MongoDB, Elasticsearch

Certifications
- AWS Solutions Architect Associate
- Certified Kubernetes Administrator
- Google Cloud Professional Cloud Architect

Soft Skills
Leadership, Communication, Problem-solving, Teamwork, Mentoring, Agile, Scrum
"""


def get_sample_jobs() -> list[dict]:
    """Return a list of sample job postings for matching."""
    return [
        {
            "id": 1,
            "title": "Senior Backend Engineer",
            "company": "TechCorp Inc.",
            "description": (
                "We are looking for a Senior Backend Engineer to design and "
                "build scalable APIs and services. You will work with a "
                "cross-functional team to deliver high-quality software."
            ),
            "required_skills": [
                "Python", "Flask", "PostgreSQL", "Docker", "AWS",
                "Redis", "CI/CD", "REST API", "Linux", "Git",
            ],
        },
        {
            "id": 2,
            "title": "Full Stack Developer",
            "company": "Startup Labs",
            "description": (
                "Join our product team as a Full Stack Developer. You will "
                "build beautiful UIs and robust backends for our SaaS platform."
            ),
            "required_skills": [
                "JavaScript", "React", "Node.js", "TypeScript",
                "PostgreSQL", "Docker", "AWS", "HTML", "CSS", "Git",
            ],
        },
        {
            "id": 3,
            "title": "Data Engineer",
            "company": "DataDriven Analytics",
            "description": (
                "Design and maintain large-scale data pipelines. Work with "
                "our data science team to deliver actionable insights."
            ),
            "required_skills": [
                "Python", "SQL", "Spark", "Airflow", "AWS",
                "Docker", "Kafka", "PostgreSQL", "Pandas", "Linux",
            ],
        },
        {
            "id": 4,
            "title": "Machine Learning Engineer",
            "company": "AI Solutions Corp",
            "description": (
                "Build and deploy ML models at scale. Collaborate with "
                "research and product teams to integrate AI into products."
            ),
            "required_skills": [
                "Python", "TensorFlow", "PyTorch", "Scikit-learn",
                "Docker", "AWS", "SQL", "Pandas", "NumPy", "Kubernetes",
            ],
        },
        {
            "id": 5,
            "title": "DevOps Engineer",
            "company": "CloudScale Systems",
            "description": (
                "Manage cloud infrastructure and CI/CD pipelines. Ensure "
                "high availability and security of production systems."
            ),
            "required_skills": [
                "Docker", "Kubernetes", "AWS", "Terraform", "Linux",
                "Jenkins", "GitHub Actions", "Python", "Bash", "Nginx",
            ],
        },
    ]
