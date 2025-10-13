"""
Test script for resume processing pipeline
==========================================

This script tests the resume processing functionality on sample files
from the dataset.
"""

import os
import json
from pathlib import Path
from resume_processor import ResumeProcessor


def test_single_resume():
    """Test processing a single resume file."""
    print("Testing single resume processing...")
    
    processor = ResumeProcessor()
    resume_dir = Path("/Users/suhasbajjuri/MyData/College FIles/Year III/SEM-5/Assignments/NLP/palaksood97/resume-dataset/versions/1/Resumes")
    
    # Get the first resume file
    resume_files = list(resume_dir.glob("*.docx"))
    if not resume_files:
        print("No resume files found!")
        return
    
    test_file = resume_files[0]
    print(f"Testing with file: {test_file.name}")
    
    # Process the resume
    result = processor.process_resume(str(test_file))
    
    if result:
        print("✅ Successfully processed resume!")
        print(f"File: {result['file_name']}")
        print(f"Text length: {result['text_length']} characters")
        
        print("\n📄 Text Preview:")
        print("-" * 50)
        print(result['raw_text'])
        print("-" * 50)
        
        print("\n🔍 Extracted Entities:")
        for entity_type, values in result['entities'].items():
            if values:
                print(f"  {entity_type.upper()}: {values}")
        
        # Save result to file for inspection
        output_file = "sample_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Full result saved to: {output_file}")
        
    else:
        print("❌ Failed to process resume")


def test_batch_processing():
    """Test batch processing of multiple resumes."""
    print("\nTesting batch processing...")
    
    processor = ResumeProcessor()
    resume_dir = Path("/Users/suhasbajjuri/MyData/College FIles/Year III/SEM-5/Assignments/NLP/palaksood97/resume-dataset/versions/1/Resumes")
    
    # Process first 5 resumes
    results = []
    resume_files = list(resume_dir.glob("*.docx"))[:5]
    
    for file_path in resume_files:
        print(f"Processing: {file_path.name}")
        result = processor.process_resume(str(file_path))
        if result:
            results.append(result)
    
    if results:
        print(f"\n✅ Successfully processed {len(results)} resumes")
        
        # Create summary
        summary = {
            'total_processed': len(results),
            'avg_text_length': sum(r['text_length'] for r in results) / len(results),
            'entities_found': {}
        }
        
        # Count entity types found
        for result in results:
            for entity_type, values in result['entities'].items():
                if values:
                    if entity_type not in summary['entities_found']:
                        summary['entities_found'][entity_type] = 0
                    summary['entities_found'][entity_type] += len(values)
        
        print("\n📊 Processing Summary:")
        print(f"  Total resumes processed: {summary['total_processed']}")
        print(f"  Average text length: {summary['avg_text_length']:.0f} characters")
        print("  Entities found:")
        for entity_type, count in summary['entities_found'].items():
            print(f"    {entity_type}: {count} instances")
        
        # Save batch results
        batch_output = "batch_results.json"
        with open(batch_output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Batch results saved to: {batch_output}")
        
    else:
        print("❌ No resumes were successfully processed")


def analyze_skill_patterns():
    """Analyze common skills found across resumes."""
    print("\nAnalyzing skill patterns...")
    
    processor = ResumeProcessor()
    resume_dir = Path("/Users/suhasbajjuri/MyData/College FIles/Year III/SEM-5/Assignments/NLP/palaksood97/resume-dataset/versions/1/Resumes")
    
    # Process more resumes for skill analysis
    all_skills = set()
    skill_count = {}
    
    resume_files = list(resume_dir.glob("*.docx"))[:10]  # First 10 resumes
    
    for file_path in resume_files:
        result = processor.process_resume(str(file_path))
        if result and result['entities']['skills']:
            for skill in result['entities']['skills']:
                all_skills.add(skill)
                skill_count[skill] = skill_count.get(skill, 0) + 1
    
    if all_skills:
        print(f"✅ Found {len(all_skills)} unique skills across {len(resume_files)} resumes")
        
        # Sort by frequency
        sorted_skills = sorted(skill_count.items(), key=lambda x: x[1], reverse=True)
        
        print("\n🔥 Most common skills:")
        for skill, count in sorted_skills[:10]:
            print(f"  {skill}: {count} times")
            
    else:
        print("❌ No skills found")


def main():
    """Run all tests."""
    print("🧪 Resume Processing Pipeline Tests")
    print("=" * 50)
    
    try:
        test_single_resume()
        test_batch_processing()
        analyze_skill_patterns()
        
        print("\n✅ All tests completed successfully!")
        print("\nNext steps:")
        print("1. Install required dependencies: pip install -r requirements.txt")
        print("2. Download spaCy model: python -m spacy download en_core_web_sm")
        print("3. For PDF OCR support, install Tesseract: brew install tesseract (macOS)")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        print("Make sure to install required dependencies first.")


if __name__ == "__main__":
    main()
