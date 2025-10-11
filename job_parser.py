import spacy
from spacy.matcher import Matcher, PhraseMatcher
import re
import json

# Load the pre-trained spaCy model
# We disable components we don't need for this task to speed up processing
nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])

# --- Skill Extraction Setup (Highly Efficient) ---

# 1. Your comprehensive list of skills
TECH_SKILLS = ["Java", "Java 8", "Core Java", "J2EE", "Spring", "Spring Boot", "Spring Cloud", "Spring MVC", "Hibernate","JPA", "Microservices", "RESTful services", "RESTful Web Services", "REST API", "API gateway", "Docker","Kubernetes", "Jenkins", "GitLab CI", "SQL", "NoSQL", "Git", "Github", "JSP", "Servlets", "Struts","React", "React.Js", "Angular", "Vue.js", "Next.js", "NodeJS", "Redux", "Kotlin", "TypeScript", "GraphQL","Python", "machine learning", "Deep Learning", "TensorFlow", "PyTorch", "Computer Vision", "OpenCV","YOLO", "Detectron2", "NLP", "Generative AI", "LLMs", "Data Engineering", "ETL Pipelines", "Big Data","Hadoop", "Spark", "AWS", "Azure Functions", "EC2", "Lambda", "RDS", "S3", "Azure", "GCP", "MongoDB","MySQL", "Oracle 12c", "PostgreSQL", "SQLite", "Elasticsearch", "Redis", "RabbitMQ", "Kafka", "Apache Kafka", "CI/CD Pipelines", "Terraform", "Ansible", "Prometheus", "Grafana", "CircleCI", "Travis CI", "Bitbucket", "Swagger", "OAuth2", "WebSockets", "Webpack", "Babel", "SASS", "SCSS", "Tailwind CSS", "Material UI", "Chakra UI", "Bootstrap", "Figma", "Wireframing", "Data Visualization", "Tableau", "PowerBI", "Qlik", "MicroStrategy", "MLOps", "MLflow", "Kubeflow", "AutoML", "Data Lake", "Blockchain", "Solidity", "Ethereum", "Smart Contracts", "Quantum Computing", "Cybersecurity", "Penetration Testing", "Ethical Hacking", "Zero Trust Architecture", "Serverless Computing", "Kubernetes Operators", "Istio", "Domain Driven Design", "Event-Driven Architecture", "Business Intelligence", "API Management", "Kong", "Apigee", "Linux", "Linux System Administration", "DevOps", "Virtualization", "VMware", "Hyper-V", "Network Administration", "TCP/IP", "CCNA", "VPN", "DHCP", "Network Monitoring Tools", "Mobile App Development", "Android", "iOS", "Flutter", "React Native", "AR", "VR", "VFX", "Robotics", "Automation", "Artificial Intelligence", "Cloud Native Applications", "Sustainability Tech", "Carbon Accounting", "Net Zero Platforms", "Technical Writing", "Documentation", "CMS", "SEO", "HTML", "CSS", "JavaScript", "Three.js", "D3.js"]
SOFT_SKILLS = ["Communication Skills", "Public Speaking", "Problem Solving", "Critical Thinking", "Collaboration","Teamwork", "Leadership", "Adaptability", "Creativity", "Time Management", "Emotional Intelligence","Project Management", "Agile", "Scrum", "Kanban", "Teaching", "English", "Digital Marketing","Content Creation", "Social Media Management"]

# 2. Initialize the PhraseMatcher
skill_matcher = PhraseMatcher(nlp.vocab, attr='LOWER')

# 3. Create patterns for the matcher
# We use nlp.make_doc to create doc objects for each skill for efficiency
tech_patterns = [nlp.make_doc(text) for text in TECH_SKILLS]
soft_patterns = [nlp.make_doc(text) for text in SOFT_SKILLS]

skill_matcher.add("TECH_SKILLS", tech_patterns)
skill_matcher.add("SOFT_SKILLS", soft_patterns)

def extract_skills_efficiently(doc):
    """Extracts skills using the efficient PhraseMatcher."""
    matches = skill_matcher(doc)
    found_skills = set()

    for match_id, start, end in matches:
        rule_id = nlp.vocab.strings[match_id]  # e.g., "TECH_SKILLS"
        span = doc[start:end]  # The matched span
        
        skill_data = {
            "skill_name": span.text.title(),
            "original_text": span.text,
            "type": "technical" if rule_id == "TECH_SKILLS" else "soft"
        }
        # Use a tuple of items to make it hashable for the set
        found_skills.add(tuple(skill_data.items()))

    # Convert the set of tuples back to a list of dictionaries
    return [dict(t) for t in found_skills]


def extract_experience(text):
    """Extracts minimum and maximum years of experience required."""
    pattern = re.compile(r'(\d+)\s*(?:-|to)\s*(\d+)\s+years?|(\d+)\+\s+years?|(\d+)\s+years?', re.IGNORECASE)
    matches = pattern.findall(text)
    min_years, max_years = None, None
    if matches:
        for match in matches:
            if match[0] and match[1]:
                min_years, max_years = int(match[0]), int(match[1])
                break
            elif match[2]:
                min_years, max_years = int(match[2]), None
                break
            elif match[3]:
                min_years, max_years = int(match[3]), int(match[3])
                break
    return {"min_years": min_years, "max_years": max_years, "description": text[:100] + "..." if text else ""}


def extract_education(doc):
    """Extracts education degree requirements from a spaCy doc."""
    matcher = Matcher(nlp.vocab)
    # **CORRECTED PATTERNS**: Using 'LOWER' is robust and fixes the error.
    patterns = [
        [{"LOWER": "bachelor"}, {"LOWER": "'s"}, {"OP": "?"}, {"LOWER": "degree"}],
        [{"LOWER": "master"}, {"LOWER": "'s"}, {"OP": "?"}, {"LOWER": "degree"}],
        [{"LOWER": "ph.d"}],
        [{"LOWER": "bs"}],
        [{"LOWER": "ms"}],
        [{"LOWER": "b.tech"}],
        [{"LOWER": "m.tech"}]
    ]
    matcher.add("EDUCATION", patterns)
    matches = matcher(doc)
    found_degrees = {doc[start:end].text for _, start, end in matches} # Use a set for automatic deduplication
    
    if not found_degrees:
        return []

    return [{"degree": degree, "field_of_study": "Computer Science, Statistics, or a related field"} for degree in found_degrees]


def parse_job_description(text):
    """
    Main function to parse a job description and return structured JSON.
    It processes the text with spaCy once and passes the 'doc' object around.
    """
    if not text:
        return {}

    # Process the text ONCE with spaCy
    doc = nlp(text)

    # Call the extraction functions with the processed doc
    skills = extract_skills_efficiently(doc)
    experience = extract_experience(text) # Regex works on raw text
    education = extract_education(doc)
    
    parsed_data = {
        "job_summary": text[:250] + "...",
        "required_skills": skills,
        "experience_requirements": experience,
        "education_requirements": education
    }
    
    return parsed_data

if __name__ == '__main__':
    from load_data import load_job_postings
    
    job_descriptions = load_job_postings()
    
    if job_descriptions:
        example_description = job_descriptions[15] # Using a different index for variety
        
        print("--- Original Job Description (Sample) ---")
        print(example_description)
        
        print("\n--- Parsed JSON Output ---")
        parsed_result = parse_job_description(example_description)
        print(json.dumps(parsed_result, indent=2))