import re
import spacy
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import List, Set
from fastapi.middleware.cors import CORSMiddleware

# --- Import Your Core & Intelligent Logic ---
from parsers.job_parser import parse_job_description
from parsers.resume_parser import extract_skills as extract_skills_from_resume_text
from parsers.resume_parser import extract_text_from_pdf, extract_text_from_docx
from intelligence.scoring import calculate_weighted_score
from intelligence.roadmap import generate_learning_roadmap

app = FastAPI(
    title="AI Skill Mapper - Final Intelligent API",
    description="The complete API that analyzes a job description against an uploaded resume file.",
    version="4.0.0",
)

# --- Add CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- NLP Model & Helper Functions ---
nlp = spacy.load("en_core_web_sm")
SKILL_NORMALIZATION_MAP = {
    "react.js": "React", "reactjs": "React", "node.js": "NodeJS", "aws": "Amazon Web Services",
    "gcp": "Google Cloud Platform", "data visualization": "Data Visualization",
    "machine learning": "Machine Learning", "analyzing data": "Data Analysis",
}

def normalize_skills(skills_list: List[dict]) -> set:
    if not skills_list: return set()
    standardized_skills = set()
    for skill_info in skills_list:
        original_skill = skill_info.get("skill_name", "").lower().strip()
        standard_name = SKILL_NORMALIZATION_MAP.get(original_skill, original_skill.title())
        standardized_skills.add(standard_name)
    return standardized_skills

def clean_text(input_text: str) -> str:
    """Removes invalid control characters that cause JSON errors."""
    return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', input_text)


# --- THE FINAL, CORRECT ENDPOINT ---
@app.post("/analyze-match-with-file", tags=["Intelligent Analysis"])
async def analyze_match_with_file_endpoint(
    job_description_text: str = Form(...),
    resume_file: UploadFile = File(...)
):
    """
    Analyzes a job description (text) against a resume (file upload)
    and generates a complete analysis and learning plan.
    """
    # Step 1: Read the uploaded resume file into memory
    resume_contents = await resume_file.read()
    filename = resume_file.filename.lower()
    resume_text = ""

    # Step 2: Extract text from the resume file based on its type
    try:
        if filename.endswith('.pdf'):
            resume_text = extract_text_from_pdf(resume_contents)
        elif filename.endswith('.docx'):
            resume_text = extract_text_from_docx(resume_contents)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload a .pdf or .docx file.")

        if not resume_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from the resume file.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume file: {e}")

    # Step 3: Clean the inputs
    job_text_cleaned = clean_text(job_description_text)
    resume_text_cleaned = clean_text(resume_text)

    # Step 4: Parse job and resume to get skills
    job_data = parse_job_description(job_text_cleaned)
    job_skills_raw = job_data.get("required_skills", [])
    resume_skills_raw = extract_skills_from_resume_text(resume_text_cleaned)

    # Step 5: Normalize skills
    resume_skills_normalized = normalize_skills(resume_skills_raw)

    # Step 6: Perform Weighted Scoring
    score_result = calculate_weighted_score(job_skills_raw, resume_skills_normalized)

    # Step 7: Generate Learning Roadmap
    missing_skills_list = [skill['skill'] for skill in score_result['details']['missing_skills']]
    learning_roadmap = generate_learning_roadmap(missing_skills_list, resume_skills_normalized)

    # Step 8: Return the final response
    return {
        "match_analysis": score_result,
        "learning_roadmap": learning_roadmap
    }
