import spacy
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

# --- Import the Core Logic from Member 1 and Member 2 ---
from parsers.job_parser import parse_job_description
from parsers.resume_parser import process_resume_file as parse_resume_from_file
# THIS IS THE NEW, CRUCIAL IMPORT for the fix
from parsers.resume_parser import extract_skills as extract_skills_from_resume_text

app = FastAPI(
    title="AI Skill Mapper - Final Intelligent API",
    description="A unified API to parse documents and intelligently analyze the match between a job and a resume.",
    version="2.0.0",
)

# --- NLP Model & Skill Normalization Engine ---
nlp = spacy.load("en_core_web_sm")

SKILL_NORMALIZATION_MAP = {
    "react.js": "React", "reactjs": "React",
    "node.js": "NodeJS", "node js": "NodeJS",
    "aws": "Amazon Web Services",
    "gcp": "Google Cloud Platform",
    "sql": "SQL", "mssql": "SQL", "my sql": "MySQL",
    "postgres": "PostgreSQL", "postgresql": "PostgreSQL",
    "machine learning": "Machine Learning", "ml": "Machine Learning",
    "deep learning": "Deep Learning", "dl": "Deep Learning",
    "natural language processing": "NLP",
    "spring boot": "Spring Boot",
    "restful webservices": "REST API", "restful services": "REST API",
    "j2ee": "Java EE",
    "python scripting": "Python",
    "analyzing data": "Data Analysis", "data analytics": "Data Analysis",
}

def normalize_skills(skills_list: List[dict]) -> set:
    """
    Takes a list of skill dictionaries and returns a clean, standardized SET of skill names.
    Using a set is highly efficient for the matching logic later.
    """
    if not skills_list:
        return set()

    standardized_skills = set()
    for skill_info in skills_list:
        original_skill = skill_info.get("skill_name", "").lower().strip()
        standard_name = SKILL_NORMALIZATION_MAP.get(original_skill, original_skill.title())
        standardized_skills.add(standard_name)
    return standardized_skills

# --- API Request and Response Models ---

class JobRequest(BaseModel):
    text: str = Field(..., example="We are looking for a Python developer...")

class MatchRequest(BaseModel):
    job_description_text: str
    resume_file_content_as_text: str

# --- Final API Endpoints ---

@app.post("/analyze-job", tags=["1. Parsing Tools"])
async def analyze_job_endpoint(request: JobRequest):
    """Parses a job description and returns its structured data."""
    return parse_job_description(request.text)

@app.post("/parse-resume", tags=["1. Parsing Tools"])
async def parse_resume_endpoint(file: UploadFile = File(...)):
    """Parses a resume file and returns its structured data."""
    contents = await file.read()
    return parse_resume_from_file(file.filename, contents)


# --- The Intelligent Matching Endpoint (NOW FIXED) ---

@app.post("/analyze-match", tags=["2. Intelligent Analysis"])
async def analyze_match_endpoint(request: MatchRequest):
    """
    Analyzes the match between a job description and a resume.
    This is the core "smart" function of the project.
    """
    # Step 1: Parse the job description to get its skills
    job_data = parse_job_description(request.job_description_text)
    job_skills_raw = job_data.get("required_skills", [])

    # Step 2: Use the CORRECT skill extractor for the resume text
    # THIS IS THE FIX: We are now using the efficient PhraseMatcher from the
    # resume parser directly on the raw text.
    resume_skills_raw = extract_skills_from_resume_text(request.resume_file_content_as_text)

    # Step 3: Normalize both sets of skills using the engine
    job_skills_normalized = normalize_skills(job_skills_raw)
    resume_skills_normalized = normalize_skills(resume_skills_raw)

    if not job_skills_normalized:
        return {"match_score": 0, "details": "No required skills found in the job description."}

    # Step 4: Calculate the match
    matching_skills = job_skills_normalized.intersection(resume_skills_normalized)
    missing_skills = job_skills_normalized.difference(resume_skills_normalized)
    
    match_score = (len(matching_skills) / len(job_skills_normalized)) * 100

    # Step 5: Return a rich, informative response
    return {
        "match_percentage": round(match_score, 2),
        "summary": f"The candidate's skills match {round(match_score, 2)}% of the job requirements.",
        "matching_skills": sorted(list(matching_skills)),
        "missing_skills_from_job": sorted(list(missing_skills)),
        "total_skills_in_resume": len(resume_skills_normalized),
        "total_skills_in_job": len(job_skills_normalized)
    }