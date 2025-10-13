import io
import re
from typing import Dict, List
import spacy
from spacy.matcher import Matcher

# File processing libraries
import docx
import fitz  # PyMuPDF

# --- NLP Model Loading (done once) ---
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading 'en_core_web_sm' model...")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# --- Helper Functions for Text Extraction ---

def extract_text_from_docx(content: bytes) -> str:
    """Extracts text from a .docx file's content."""
    doc = docx.Document(io.BytesIO(content))
    return "\n".join([para.text for para in doc.paragraphs if para.text])

def extract_text_from_pdf(content: bytes) -> str:
    """Extracts text from a .pdf file's content."""
    doc = fitz.open(stream=content, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# --- Core Logic for Entity Extraction ---

def extract_contact_info(text: str) -> Dict:
    """Extracts name, email, and phone number."""
    info = {
        "name": "Not Found",
        "email": "Not Found",
        "phone": "Not Found"
    }
    
    # Email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    if email_match:
        info["email"] = email_match.group(0)

    # Phone number (basic North American/Indian patterns)
    phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    if phone_match:
        info["phone"] = phone_match.group(0)
        
    # Name (heuristic: often the first one or two capitalized words at the start)
    doc = nlp(text[:100]) # Only process the top of the resume for the name
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            info["name"] = ent.text
            break
            
    return info

def extract_skills(text: str) -> List[dict]:
    """Uses PhraseMatcher for efficient, multi-word skill extraction."""
    # This skill list should be managed centrally or expanded
    SKILL_KEYWORDS = [
        "python", "java", "c++", "c#", "javascript", "typescript", "sql", "nosql",
        "react", "angular", "vue", "django", "flask", "spring boot", "node.js",
        "aws", "azure", "gcp", "docker", "kubernetes", "git", "jenkins", "ci/cd",
        "machine learning", "deep learning", "tensorflow", "pytorch", "pandas",
        "numpy", "scikit-learn", "data analysis", "power bi", "tableau"
    ]
    
    matcher = spacy.matcher.PhraseMatcher(nlp.vocab, attr='LOWER')
    patterns = [nlp.make_doc(text) for text in SKILL_KEYWORDS]
    matcher.add("SKILL", patterns)

    doc = nlp(text)
    matches = matcher(doc)
    
    found_skills = set()
    for _, start, end in matches:
        span = doc[start:end]
        found_skills.add(span.text)
        
    # Return in the standard format agreed upon
    return [{"skill_name": skill, "type": "technical"} for skill in found_skills]


# --- Main Processing Function for the API ---

def process_resume_file(filename: str, content: bytes) -> Dict:
    """
    The main function to process a resume file from its content.
    This is the single "engine" function Member 3's API will call.
    """
    text = ""
    if filename.lower().endswith('.docx'):
        text = extract_text_from_docx(content)
    elif filename.lower().endswith('.pdf'):
        text = extract_text_from_pdf(content)
    else:
        raise ValueError("Unsupported file type. Please upload a .docx or .pdf file.")

    if not text.strip():
        raise ValueError("Could not extract any text from the file.")

    # Extract all pieces of information
    contact_info = extract_contact_info(text)
    skills = extract_skills(text)
    # Placeholder for other sections like experience and education
    # A full implementation would have functions similar to extract_skills for these

    # Assemble the final JSON object based on the standard schema
    return {
        "source_document": filename,
        "personal_details": contact_info,
        "professional_summary": text[:250] + "...", # A simple summary
        "skills": skills,
        "work_experience": [], # Placeholder
        "education": [] # Placeholder
    }