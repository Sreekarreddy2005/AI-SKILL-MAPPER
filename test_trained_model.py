#!/usr/bin/env python3
"""
Test the trained NER model
=========================

This script tests the trained custom NER model on resume text.
"""

import spacy
import json
from pathlib import Path

def test_trained_model():
    """Test the trained model on sample resume text."""
    print("🧪 Testing Trained NER Model")
    print("=" * 40)
    
    # Load the trained model
    try:
        nlp = spacy.load("./output/model-last")
        print("✅ Successfully loaded trained model")
    except Exception as e:
        print(f"❌ Failed to load model: {str(e)}")
        return
    
    # Sample resume text
    sample_text = """
    John Smith
    Senior Software Engineer
    Email: john.smith@email.com
    Phone: (555) 123-4567
    
    Experience:
    - Software Engineer at Microsoft (2020-2023)
    - Java Developer at Google (2018-2020)
    
    Education:
    - Bachelor of Science in Computer Science, Stanford University, 2018
    
    Skills: Java, Python, React, SQL, Agile, Scrum
    """
    
    print(f"\n📄 Sample Resume Text:")
    print("-" * 40)
    print(sample_text.strip())
    print("-" * 40)
    
    # Process with trained model
    doc = nlp(sample_text)
    
    print(f"\n🔍 Extracted Entities:")
    print("-" * 40)
    
    entities_found = {}
    for ent in doc.ents:
        if ent.label_ not in entities_found:
            entities_found[ent.label_] = []
        entities_found[ent.label_].append(ent.text)
    
    for label, texts in entities_found.items():
        print(f"{label}: {texts}")
    
    # Test with actual resume from dataset
    print(f"\n📄 Testing with Real Resume:")
    print("-" * 40)
    
    resume_dir = Path("palaksood97/resume-dataset/versions/1/Resumes")
    if resume_dir.exists():
        resume_files = list(resume_dir.glob("*.docx"))[:1]  # Just test one
        
        if resume_files:
            from resume_processor import ResumeProcessor
            processor = ResumeProcessor()
            
            resume_file = resume_files[0]
            print(f"Processing: {resume_file.name}")
            
            # Extract text
            text = processor.extract_text_from_file(str(resume_file))
            
            if text:
                # Process with trained model
                doc = nlp(text[:1000])  # First 1000 characters
                
                entities_found = {}
                for ent in doc.ents:
                    if ent.label_ not in entities_found:
                        entities_found[ent.label_] = []
                    entities_found[ent.label_].append(ent.text)
                
                print(f"\n🔍 Entities found in real resume:")
                for label, texts in entities_found.items():
                    print(f"{label}: {texts[:5]}")  # Show first 5 of each type
    
    print(f"\n✅ Model testing completed!")

if __name__ == "__main__":
    test_trained_model()
