from fastapi import FastAPI
from pydantic import BaseModel
import datetime

# Import your parser function from the other file
from job_parser import parse_job_description

# Initialize the FastAPI app
app = FastAPI(
    title="Job Description Parser API",
    description="An API to parse raw job descriptions and extract structured information.",
    version="1.0.0"
)

class JobDescriptionRequest(BaseModel):
    """The request model for the API endpoint."""
    text: str
    source_url: str | None = None # Optional field for the URL

@app.post("/parse-job/")
def parse_job(request: JobDescriptionRequest):
    """
    This endpoint accepts a block of text (the job description) and returns
    a JSON object with the extracted skills, experience, etc. [cite: 19]
    """
    raw_text = request.text
    
    # Use the NLP model to get structured data
    parsed_data = parse_job_description(raw_text)
    
    # Combine with metadata to match the final schema
    final_output = {
        "source_url": request.source_url, # [cite: 148]
        "last_updated": datetime.datetime.now().isoformat(), # [cite: 149]
        # These are placeholders; a more advanced model could extract them
        "job_details": { 
            "job_title": None, # [cite: 151]
            "company_name": None, # [cite: 152]
            "location": None # [cite: 153]
        },
        **parsed_data # Merge the parsed data
    }

    return final_output

# To run the app, use the command:
# uvicorn main.api:app --reload