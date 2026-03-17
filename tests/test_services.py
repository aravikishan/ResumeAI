"""Unit tests for parser and scorer services."""

from services.parser import (
    extract_email,
    extract_phone,
    extract_name,
    extract_skills,
    extract_experience,
    extract_education,
    extract_sections,
    detect_experience_level,
    count_action_verbs,
    get_improvement_suggestions,
    parse_resume,
)
from services.scorer import (
    calculate_ats_score,
    match_job,
    match_all_jobs,
)


class TestExtractEmail:
    def test_standard_email(self):
        assert extract_email("Contact me at john@example.com today") == "john@example.com"

    def test_no_email(self):
        assert extract_email("No email here") is None

    def test_email_with_dots(self):
        result = extract_email("john.doe.smith@company.co.uk")
        assert result is not None
        assert "@" in result


class TestExtractPhone:
    def test_us_phone(self):
        result = extract_phone("Call (555) 123-4567")
        assert result is not None
        assert "555" in result

    def test_no_phone(self):
        assert extract_phone("No phone number") is None

    def test_phone_with_dashes(self):
        result = extract_phone("555-123-4567")
        assert result is not None


class TestExtractName:
    def test_standard_name(self):
        text = "John Anderson\nSoftware Engineer\nemail@test.com"
        assert extract_name(text) == "John Anderson"

    def test_no_name(self):
        text = "skills: python, java"
        result = extract_name(text)
        assert result is None or isinstance(result, str)


class TestExtractSkills:
    def test_programming_skills(self):
        text = "I know Python, Java, and JavaScript"
        skills = extract_skills(text)
        assert "Programming" in skills
        assert "Python" in skills["Programming"]

    def test_framework_skills(self):
        text = "Experience with React, Flask, and Node.js"
        skills = extract_skills(text)
        assert "Frameworks" in skills

    def test_cloud_skills(self):
        text = "Deployed on AWS using Docker and Kubernetes"
        skills = extract_skills(text)
        assert "Cloud" in skills
        assert "AWS" in skills["Cloud"]

    def test_no_skills(self):
        text = "Just some random text with no tech terms."
        skills = extract_skills(text)
        assert len(skills) == 0 or all(len(v) == 0 for v in skills.values())

    def test_multiple_categories(self):
        text = "Python React AWS PostgreSQL Leadership"
        skills = extract_skills(text)
        assert len(skills) >= 3


class TestExtractExperience:
    def test_years_pattern(self):
        text = "8 years of experience in software development"
        assert extract_experience(text) == 8.0

    def test_no_experience(self):
        assert extract_experience("No experience mentioned") is None

    def test_multiple_years(self):
        text = "3 years in Java, 5 years of experience total"
        result = extract_experience(text)
        assert result == 5.0


class TestExtractEducation:
    def test_bachelors(self):
        text = "Bachelor of Science in Computer Science"
        assert extract_education(text) == "Bachelor of Science"

    def test_masters(self):
        text = "Master of Science in Data Analytics"
        assert extract_education(text) == "Master of Science"

    def test_phd(self):
        text = "Ph.D in Machine Learning"
        assert extract_education(text) == "PhD"

    def test_no_education(self):
        assert extract_education("No degree listed") is None


class TestExtractSections:
    def test_finds_sections(self):
        text = """Name
Summary
A professional summary here.

Experience
Worked at TechCorp for 5 years.

Skills
Python, Java
"""
        sections = extract_sections(text)
        assert "summary" in sections
        assert "experience" in sections
        assert "skills" in sections

    def test_empty_text(self):
        sections = extract_sections("")
        assert len(sections) == 0


class TestExperienceLevel:
    def test_entry(self):
        assert detect_experience_level(1.0) == "Entry"

    def test_mid(self):
        assert detect_experience_level(4.0) == "Mid"

    def test_senior(self):
        assert detect_experience_level(8.0) == "Senior"

    def test_lead(self):
        assert detect_experience_level(15.0) == "Lead"

    def test_unknown(self):
        assert detect_experience_level(None) == "Unknown"


class TestActionVerbs:
    def test_counts_verbs(self):
        text = "Led a team. Developed APIs. Managed deployments. Built systems."
        count = count_action_verbs(text)
        assert count >= 4


class TestSuggestions:
    def test_incomplete_resume(self):
        parsed = {"skills": {}, "sections": {}}
        suggestions = get_improvement_suggestions(parsed)
        assert len(suggestions) > 0

    def test_complete_resume(self):
        parsed = {
            "name": "John Doe",
            "email": "john@test.com",
            "phone": "555-1234",
            "skills": {
                "Programming": ["Python", "Java", "JavaScript"],
                "Cloud": ["AWS", "Docker"],
                "Soft Skills": ["Leadership"],
            },
            "education": "Bachelor of Science",
            "experience_years": 5.0,
            "sections": {"summary": "text", "experience": "text", "certifications": "text"},
        }
        suggestions = get_improvement_suggestions(parsed)
        # Should have few or positive suggestions for a complete resume
        assert isinstance(suggestions, list)


class TestATSScore:
    def test_full_resume(self):
        parsed = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "555-1234",
            "skills": {
                "Programming": ["Python", "Java"],
                "Frameworks": ["React"],
                "Cloud": ["AWS"],
                "Databases": ["PostgreSQL"],
            },
            "experience_years": 5.0,
            "education": "Bachelor of Science",
            "sections": {"summary": "x", "experience": "x", "skills": "x"},
        }
        score, breakdown = calculate_ats_score(parsed, raw_text="Led team. Built system. Developed API. Managed project. Created pipeline. Deployed apps. Improved performance. Designed architecture. Sample resume text with enough words.")
        assert 50 <= score <= 100
        assert breakdown["contact_email"] == 10
        assert breakdown["contact_phone"] == 10

    def test_empty_resume(self):
        parsed = {"skills": {}}
        score, breakdown = calculate_ats_score(parsed)
        assert score == 0

    def test_partial_resume(self):
        parsed = {
            "email": "test@test.com",
            "skills": {"Programming": ["Python"]},
        }
        score, breakdown = calculate_ats_score(parsed)
        assert 10 < score < 50


class TestJobMatching:
    def test_good_match(self):
        parsed = {
            "skills": {
                "Programming": ["Python"],
                "Frameworks": ["Flask"],
                "Cloud": ["Docker", "AWS"],
                "Databases": ["PostgreSQL", "Redis"],
            }
        }
        job = {
            "title": "Backend Engineer",
            "required_skills": ["Python", "Flask", "PostgreSQL", "Docker", "AWS"],
        }
        result = match_job(parsed, job)
        assert result["match_percentage"] == 100.0
        assert len(result["missing_skills"]) == 0

    def test_partial_match(self):
        parsed = {
            "skills": {"Programming": ["Python", "Java"]}
        }
        job = {
            "title": "Full Stack",
            "required_skills": ["Python", "React", "Node.js", "PostgreSQL"],
        }
        result = match_job(parsed, job)
        assert 0 < result["match_percentage"] < 100
        assert len(result["missing_skills"]) > 0

    def test_no_match(self):
        parsed = {"skills": {}}
        job = {
            "title": "Developer",
            "required_skills": ["Python", "Flask"],
        }
        result = match_job(parsed, job)
        assert result["match_percentage"] == 0.0

    def test_match_all_sorted(self):
        parsed = {
            "skills": {"Programming": ["Python"], "Cloud": ["Docker", "AWS"]}
        }
        jobs = [
            {"id": 1, "title": "Job A", "required_skills": ["Ruby", "Rails"]},
            {"id": 2, "title": "Job B", "required_skills": ["Python", "Docker", "AWS"]},
        ]
        results = match_all_jobs(parsed, jobs)
        assert results[0]["match_percentage"] >= results[1]["match_percentage"]


class TestParseResume:
    def test_full_parse(self):
        text = """John Doe
Software Engineer
Email: john@example.com
Phone: (555) 111-2222

Summary
Experienced developer with 5 years of experience in Python and Flask.

Experience
5 years of experience in software development.
Led team of 4 engineers. Built microservices architecture.

Education
Bachelor of Science in Computer Science

Skills
Python, Flask, React, AWS, Docker, PostgreSQL
Leadership and Communication skills.

Certifications
AWS Solutions Architect
"""
        result = parse_resume(text)
        assert result["email"] == "john@example.com"
        assert "skills" in result
        assert "sections" in result
        assert result["experience_level"] in ("Entry", "Mid", "Senior", "Lead", "Unknown")
