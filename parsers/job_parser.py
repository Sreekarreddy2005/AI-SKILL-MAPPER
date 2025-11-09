import spacy
from spacy.matcher import PhraseMatcher
import re

# Load a light spaCy pipeline (disable what we don't need)
nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])

# -------------------------------
# Skill dictionaries (editable)
# -------------------------------
TECH_SKILLS = [
    # Languages
    "Java", "Python", "JavaScript", "TypeScript", "SQL",

    # Back-end / Frameworks
    "Spring", "Spring Boot", "Hibernate", "JPA",
    "NodeJS", "Node.js", "Express", "Express.js",
    "Django", "Flask", "FastAPI", "Fast Api",

    # Front-end
    "React", "React.js", "Angular", "Vue", "HTML", "CSS", "Tailwind", "Bootstrap",

    # APIs
    "REST", "REST API", "RESTful Services", "RESTful Web Services", "OpenAPI", "Swagger", "gRPC", "OAuth", "JWT",

    # Databases
    "MySQL", "PostgreSQL", "MongoDB", "Oracle", "SQL Server", "Redis", "Elasticsearch",

    # Cloud & DevOps
    "AWS", "Amazon Web Services", "GCP", "Google Cloud Platform", "Azure",
    "Docker", "Kubernetes", "Terraform", "Ansible",
    "CI/CD", "Git", "GitHub", "GitLab", "GitLab CI", "Jenkins",

    # Data / Analytics
    "PowerBI", "Power BI", "Tableau", "Data Visualization", "ETL",

    # Big Data / Streaming
    "Kafka", "Hadoop", "Spark", "Airflow",

    # ML / AI
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch",
    "Pandas", "NumPy", "Matplotlib", "scikit-learn",

    # Monitoring/Observability
    "Prometheus", "Grafana", "Sentry", "OpenTelemetry",

    # Web Servers / Infra
    "Nginx", "NGINX", "Apache", "Tomcat",

    # Misc
    "Postman", "Figma", "OpenAPI", "Swagger"
]

SOFT_SKILLS = [
    "Communication", "Communication Skills", "Public Speaking",
    "Problem Solving", "Teamwork", "Collaboration", "Leadership",
    "Time Management", "Adaptability", "Critical Thinking",
    "Creativity", "Attention to Detail", "Stakeholder Management",
    "Presentation Skills", "Mentoring", "Coaching",
    "Decision Making", "Negotiation", "Conflict Resolution",
    "Writing", "Documentation", "Agile", "Scrum"
]

def _build_phrase_matcher(nlp, phrases, label):
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [nlp.make_doc(p) for p in phrases]
    matcher.add(label, patterns)
    return matcher

TECH_MATCHER = _build_phrase_matcher(nlp, TECH_SKILLS, "TECH_SKILLS")
SOFT_MATCHER = _build_phrase_matcher(nlp, SOFT_SKILLS, "SOFT_SKILLS")


def _extract_skills(doc):
    """Fast extraction using PhraseMatcher; keeps raw text (no title-casing)."""
    matches = TECH_MATCHER(doc) + SOFT_MATCHER(doc)
    seen = set()   # de-dupe identical spans

    results = []
    for match_id, start, end in matches:
        label = nlp.vocab.strings[match_id]  # "TECH_SKILLS" or "SOFT_SKILLS"
        span = doc[start:end]

        # Keep original text; only trim whitespace.
        skill = span.text.strip()
        if not skill:
            continue

        key = (skill.lower(), label)
        if key in seen:
            continue
        seen.add(key)

        results.append({
            "skill_name": skill,
            "original_text": span.text,
            "type": "technical" if label == "TECH_SKILLS" else "soft"
        })
    return results


def parse_job_description(job_text: str) -> dict:
    """
    Returns:
      {
        "title": str,
        "location": str,
        "experience": str,
        "required_skills": [ {skill_name, original_text, type}, ... ],
        "raw_text": str
      }
    """
    text = (job_text or "").strip()
    if not text:
        return {
            "title": "",
            "location": "",
            "experience": "",
            "required_skills": [],
            "raw_text": ""
        }

    doc = nlp(text)

    # Lightweight heuristics for metadata
    title = ""
    m = re.search(r"(?:^|\n)\s*(?:Title|Position)\s*:\s*(.+)", text, flags=re.IGNORECASE)
    if m:
        title = m.group(1).strip()

    location = ""
    m = re.search(r"(?:^|\n)\s*Location\s*:\s*([^\n,]+)", text, flags=re.IGNORECASE)
    if m:
        location = m.group(1).strip()

    experience = ""
    m = re.search(r"(\d+)\+?\s*(?:years|yrs|yr)", text, flags=re.IGNORECASE)
    if m:
        experience = m.group(1).strip()

    required_skills = _extract_skills(doc)

    return {
        "title": title,
        "location": location,
        "experience": experience,
        "required_skills": required_skills,
        "raw_text": text
    }
