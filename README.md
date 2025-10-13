# AI Skill Mapper
An intelligent backend system that uses Natural Language Processing (NLP) to parse, understand, and analyze the match between job descriptions and candidate resumes.

# Overview
The AI Skill Mapper is a unified API designed to automate the initial stages of the recruitment pipeline. It ingests unstructured text from job postings and resume files (.pdf, .docx), extracts key information, and provides an objective match analysis based on required skills. This saves recruiters time, reduces manual effort, and helps identify qualified candidates more efficiently.

# Key Features
 Job Description Parsing: Extracts required skills, experience, and education from job postings.

Multi-Format Resume Parsing: Processes .pdf and .docx files to extract candidate details, contact information, and listed skills.

Intelligent Skill Normalization: A core engine that understands variations of skills (e.g., "React.js", "ReactJS") and maps them to a standardized name for accurate comparison.

Automated Match Analysis: A dedicated API endpoint that calculates a percentage match score between a job's requirements and a candidate's skills, providing a detailed breakdown of matching and missing skills.

# Technology Stack

Backend Framework: FastAPI

NLP Library: spaCy

File Processing: PyMuPDF (for PDFs), python-docx (for Word documents)

Server: Uvicorn

Data Handling: Pydantic

# Setup:-
1) Clone the repo
2) Activate venv:- python -m venv venv
.\venv\Scripts\activate
3) Run this command to install neccessary libraries:- pip install -r requirements.txt and 
python -m spacy download en_core_web_sm
4) On your active venv platform install another library:- pip install python-multipart
5) Install the requirements:- pip install -r requirements.txt
6) Run the main.py in termnial using :- uvicorn main:app --reload

# TESTING:- 
1) After starting the server go to http://127.0.0.1:8000/docs
2) Click on analyze-job section and expalnd it and click on Try it out and eneter sample text eg:- {
  "text": "We are seeking a full-stack engineer with solid experience in Python and creating REST APIs. Cloud skills in Amazon Web Services (AWS) are a must. The candidate should be proficient with Docker for containerization and have frontend experience with React."} and click on execute button and you will get ooutput 200 (Success)
3) Click on parse-resume section and expalnd it and click on Try it out and upload your resume pdf
4) Click on analyze-match section and expalnd it and click on Try it out and enter sample text:- {
  "job_description_text": "We are seeking a full-stack engineer with solid experience in Python and creating REST APIs. Cloud skills in Amazon Web Services (AWS) are a must. The candidate should be proficient with Docker for containerization and have frontend experience with React.",
  "resume_file_content_as_text": "A skilled software developer with a strong background in Python and building RESTful services. Experienced in cloud deployment using AWS and containerizing applications with Docker. Previously worked on backend systems."
} and then u will see output with match percentage

   
