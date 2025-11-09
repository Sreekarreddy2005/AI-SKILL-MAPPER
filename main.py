import re
import spacy
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Set

# --- Import Your Core & Intelligent Logic ---
from parsers.job_parser import parse_job_description
from parsers.resume_parser import extract_skills as extract_skills_from_resume_text
from parsers.resume_parser import extract_text_from_pdf, extract_text_from_docx
from intelligence.scoring import calculate_weighted_score
from intelligence.roadmap import generate_learning_roadmap

app = FastAPI(
    title="AI Skill Mapper - Final Intelligent API",
    description="Analyzes JD vs Resume, scores match, and suggests a learning roadmap.",
    version="1.0.0"
)

# CORS (loose for local dev; restrict in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Normalization & helpers
# -------------------------------
nlp = spacy.load("en_core_web_sm")

SKILL_NORMALIZATION_MAP = {
    # Clouds
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "GCP",
    "google cloud platform": "GCP",
    "azure": "Azure",

    # Web/JS
    "react": "React",
    "react.js": "React",
    "reactjs": "React",
    "nodejs": "NodeJS",
    "node.js": "NodeJS",
    "javascript": "JavaScript",
    "typescript": "TypeScript",

    # APIs  (collapse to one canonical to avoid double counting)
    "rest": "REST API",
    "rest api": "REST API",
    "rest apis": "REST API",
    "restful api": "REST API",
    "restful apis": "REST API",
    "restful services": "REST API",
    "restful web services": "REST API",
    "api": "API",
    "openapi": "OpenAPI",
    "swagger": "Swagger",

    # DevOps / CI
    "ci/cd": "CI/CD",
    "gitlab ci": "GitLab CI",
    "gitlab": "GitLab",
    "git": "GIT",

    # Data / BI
    "power bi": "PowerBI",
    "powerbi": "PowerBI",
    "tableau": "Tableau",
    "data visualization": "Data Visualization",

    # ML/AI
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",

    # Runtimes / Frameworks
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "express": "Express",
    "express.js": "Express",

    # Containers / Infra
    "docker": "Docker",
    "kubernetes": "Kubernetes",

    # Databases (include common variants)
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "postgre sql": "PostgreSQL",
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "mongo db": "MongoDB",

    # Common short skills
    "css": "CSS",
    "html": "HTML",
    "sql": "SQL",

    # Languages
    "java": "Java",
    "python": "Python"
}

def normalize_skill_name(name: str) -> str:
    s = (name or "").strip().lower()
    if not s:
        return ""
    if s in SKILL_NORMALIZATION_MAP:
        return SKILL_NORMALIZATION_MAP[s]
    # Short alphabetic tokens -> uppercase (css, sql, git)
    if s.isalpha() and len(s) <= 4:
        return s.upper()
    # Default Title Case (acronyms protected by the map/rule above)
    return s.title()

def normalize_resume_skills(skills_list: List[dict]) -> set:
    """Normalize and return a SET of resume skills (unique, canonical)."""
    if not skills_list:
        return set()
    out = set()
    for sk in skills_list:
        canon = normalize_skill_name(sk.get("skill_name", ""))
        if canon:
            out.add(canon)
    return out

def normalize_job_skills(job_skills: List[dict]) -> List[dict]:
    """
    Normalize AND de-duplicate by canonical name so
    'React' + 'React.js' don't appear twice.
    """
    seen = {}
    for sk in job_skills or []:
        canon = normalize_skill_name(sk.get("skill_name", ""))
        if not canon:
            continue
        if canon not in seen:
            seen[canon] = {**sk, "skill_name": canon}
        else:
            # prefer 'technical' if any variant is technical
            prev_type = seen[canon].get("type", "technical")
            new_type = sk.get("type", prev_type)
            if prev_type != "technical" and new_type == "technical":
                seen[canon] = {**sk, "skill_name": canon}
    return list(seen.values())

def clean_text(s: str) -> str:
    """Remove control chars that can break JSON/parsing."""
    return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', s or "")

# -------------------------------
# Endpoint
# -------------------------------
@app.post("/analyze-match-with-file", tags=["Intelligent Analysis"])
async def analyze_match_with_file_endpoint(
    job_description_text: str = Form(...),
    resume_file: UploadFile = File(...)
):
    """
    Analyze a job description (text) vs a resume (file) and
    return match analysis + learning roadmap.
    """
    # Step 1: Read resume
    try:
        blob = await resume_file.read()
        filename = (resume_file.filename or "").lower()

        if filename.endswith(".pdf"):
            resume_text = extract_text_from_pdf(blob)
        elif filename.endswith(".docx"):
            resume_text = extract_text_from_docx(blob)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload a .pdf or .docx file.")

        if not resume_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from the resume file.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume file: {e}")

    # Step 2: Clean inputs
    job_text = clean_text(job_description_text)
    resume_text = clean_text(resume_text)

    # Step 3: Parse JD + resume skills
    job_data = parse_job_description(job_text)
    job_skills_raw = job_data.get("required_skills", [])
    resume_skills_raw = extract_skills_from_resume_text(resume_text)

    # Step 4: Normalize both sides
    job_skills = normalize_job_skills(job_skills_raw)
    resume_skills = normalize_resume_skills(resume_skills_raw)

    # -------- Optional but recommended fallback --------
    # Some PDF parsers or custom resumes use variants; capture them from raw text.
    FALLBACK_RESUME_KEYWORDS = {
        # Acronyms / short terms
        r"\bcss\b": "CSS",
        r"\bci/cd\b": "CI/CD",
        r"\bgitlab\b": "GitLab",
        r"\bfastapi\b": "FastAPI",

        # RESTful variants
        r"\brestful\s*api(s)?\b": "REST API",
        r"\brest\s*api(s)?\b": "REST API",

        # Databases: common variants/spacing
        r"\bmongo\s*db\b": "MongoDB",
        r"\bmongodb\b": "MongoDB",
        r"\bpostgres(?:ql)?\b": "PostgreSQL",
        r"\bpostgre\s*sql\b": "PostgreSQL",
    }
    for pat, canon in FALLBACK_RESUME_KEYWORDS.items():
        if re.search(pat, resume_text, flags=re.IGNORECASE):
            resume_skills.add(canon)
    # -------- /fallback --------

    # Step 5: Score
    score_result = calculate_weighted_score(job_skills, resume_skills)

    # Step 6: Roadmap
    missing = [x["skill"] for x in score_result["details"]["missing_skills"]]
    roadmap = generate_learning_roadmap(missing, resume_skills)

    return {
        "match_analysis": score_result,
        "learning_roadmap": roadmap
    }
