import spacy
from spacy.tokens import DocBin
from tqdm import tqdm
import json
import random
import os
from pathlib import Path
from resume_processor import ResumeProcessor

# --- Training Data Generation from Resume Dataset ---
def generate_training_data_from_resumes():
    """Generate training data from the resume dataset."""
    print("Generating training data from resume dataset...")
    
    processor = ResumeProcessor()
    resume_dir = Path("palaksood97/resume-dataset/versions/1/Resumes")
    
    if not resume_dir.exists():
        print(f"❌ Resume dataset not found at: {resume_dir}")
        return []
    
    # Get resume files
    resume_files = list(resume_dir.glob("*.docx")) + list(resume_dir.glob("*.DOCX"))
    
    if not resume_files:
        print(f"❌ No resume files found")
        return []
    
    training_data = []
    
    # Process first 20 resumes for training data
    for i, resume_file in enumerate(resume_files[:20]):
        try:
            print(f"Processing {i+1}/20: {resume_file.name}")
            
            # Extract text
            text = processor.extract_text_from_file(str(resume_file))
            
            if not text or len(text.strip()) < 50:
                continue
            
            # Extract entities using the processor
            entities = processor.extract_entities(text)
            
            # Convert to spaCy training format with overlap checking
            spacy_entities = []
            used_positions = set()
            
            # Helper function to check for overlaps
            def has_overlap(start, end):
                for pos in range(start, end):
                    if pos in used_positions:
                        return True
                return False
            
            # Helper function to mark positions as used
            def mark_used(start, end):
                for pos in range(start, end):
                    used_positions.add(pos)
            
            # Add email entities (highest priority)
            for email in entities.get('emails', []):
                start = text.find(email)
                if start != -1 and not has_overlap(start, start + len(email)):
                    spacy_entities.append((start, start + len(email), "EMAIL"))
                    mark_used(start, start + len(email))
            
            # Add phone entities (high priority)
            for phone in entities.get('phones', []):
                start = text.find(phone)
                if start != -1 and not has_overlap(start, start + len(phone)):
                    spacy_entities.append((start, start + len(phone), "PHONE"))
                    mark_used(start, start + len(phone))
            
            # Add skill entities (medium priority)
            for skill in entities.get('skills', []):
                if len(skill) > 2:  # Only add skills longer than 2 characters
                    start = text.find(skill)
                    if start != -1 and not has_overlap(start, start + len(skill)):
                        spacy_entities.append((start, start + len(skill), "SKILL"))
                        mark_used(start, start + len(skill))
            
            # Add education entities (medium priority)
            for edu in entities.get('education', []):
                if len(edu) > 3:  # Only add education longer than 3 characters
                    start = text.find(edu)
                    if start != -1 and not has_overlap(start, start + len(edu)):
                        spacy_entities.append((start, start + len(edu), "EDUCATION"))
                        mark_used(start, start + len(edu))
            
            # Add date entities (low priority)
            for date in entities.get('dates', []):
                if len(date) > 2:  # Only add dates longer than 2 characters
                    start = text.find(date)
                    if start != -1 and not has_overlap(start, start + len(date)):
                        spacy_entities.append((start, start + len(date), "DATE"))
                        mark_used(start, start + len(date))
            
            # Add company entities (lowest priority, filter out common words)
            common_words = {'the', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            for company in entities.get('companies', []):
                if (len(company) > 3 and 
                    company.lower() not in common_words and 
                    not company.isdigit()):
                    start = text.find(company)
                    if start != -1 and not has_overlap(start, start + len(company)):
                        spacy_entities.append((start, start + len(company), "ORG"))
                        mark_used(start, start + len(company))
            
            # Only add if we have at least 2 entities
            if len(spacy_entities) >= 2:
                training_data.append((text, {"entities": spacy_entities}))
                
        except Exception as e:
            print(f"Error processing {resume_file.name}: {str(e)}")
            continue
    
    print(f"✅ Generated {len(training_data)} training examples")
    return training_data

# --- Placeholder for Manual Annotated Data ---
MANUAL_TRAIN_DATA = [
    # (Text, {"entities": [(start_offset, end_offset, entity_label), ...]})
    ("Alice Johnson worked as a Software Engineer at Google from 2018-2023. Her email is aj@gmail.com.", {
        "entities": [
            (0, 14, "NAME"),
            (32, 51, "JOB_TITLE"),
            (55, 61, "ORG"),
            (67, 76, "DATES"),
            (93, 103, "EMAIL")
        ]
    }),
    ("Skills: Python, TensorFlow, and SQL. Education: B.S. CompSci, MIT, 2017-2021.", {
        "entities": [
            (8, 14, "SKILL"),
            (16, 26, "SKILL"),
            (32, 35, "SKILL"),
            (50, 63, "DEGREE"),
            (65, 68, "ORG"),
            (70, 79, "DATES")
        ]
    }),
    ("John Smith, Phone: (555) 123-4567, Email: john.smith@email.com", {
        "entities": [
            (0, 10, "NAME"),
            (18, 32, "PHONE"),
            (44, 65, "EMAIL")
        ]
    }),
    ("Bachelor of Science in Computer Science from Stanford University, 2020", {
        "entities": [
            (0, 27, "EDUCATION"),
            (32, 50, "ORG"),
            (52, 56, "DATE")
        ]
    }),
    ("Experience: Senior Developer at Microsoft (2021-2023), Java, Python, React", {
        "entities": [
            (12, 28, "JOB_TITLE"),
            (32, 41, "ORG"),
            (43, 52, "DATES"),
            (54, 58, "SKILL"),
            (60, 66, "SKILL"),
            (68, 73, "SKILL")
        ]
    })
]

def train_ner_model(train_data):
    """Train a custom NER model using spaCy."""
    if len(train_data) < 5:
        print("❌ Not enough training data. Need at least 5 examples.")
        return False
    
    print(f"📊 Training with {len(train_data)} examples")
    
    # 1. Prepare Data for Training (Converting to spaCy's binary format)
    # Shuffle and split your data into training and development sets (e.g., 80/20)
    random.shuffle(train_data)
    split_point = int(len(train_data) * 0.8)
    training_examples = train_data[:split_point]
    dev_examples = train_data[split_point:] if len(train_data) > 1 else train_data

    print(f"📈 Training examples: {len(training_examples)}")
    print(f"📈 Dev examples: {len(dev_examples)}")

    # Create DocBin objects for efficient serialization
    nlp = spacy.blank("en")
    db_train = DocBin()
    
    for text, annot in tqdm(training_examples, desc="Creating Training Data"):
        doc = nlp.make_doc(text)
        entities = annot["entities"]
        spans = [doc.char_span(start, end, label=label) for start, end, label in entities]
        doc.ents = [span for span in spans if span is not None] # Filter out None spans
        db_train.add(doc)
    
    db_train.to_disk("./train.spacy") # Save training data to disk
    print("✅ Training data saved to train.spacy")

    db_dev = DocBin()
    for text, annot in tqdm(dev_examples, desc="Creating Dev Data"):
        doc = nlp.make_doc(text)
        entities = annot["entities"]
        spans = [doc.char_span(start, end, label=label) for start, end, label in entities]
        doc.ents = [span for span in spans if span is not None]
        db_dev.add(doc)
    
    db_dev.to_disk("./dev.spacy") # Save development data to disk
    print("✅ Dev data saved to dev.spacy")

    # 2. Create config file for training
    create_training_config()
    
    # 3. Start the Training Process
    print("\n🚀 Starting spaCy training...")
    
    # Run training command
    import subprocess
    try:
        cmd = [
            "python3", "-m", "spacy", "train", 
            "base_config.cfg", 
            "--output", "./output", 
            "--paths.train", "./train.spacy", 
            "--paths.dev", "./dev.spacy"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Training completed successfully!")
            print("📁 Model saved to: ./output/model-best")
            return True
        else:
            print(f"❌ Training failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running training: {str(e)}")
        return False

def create_training_config():
    """Create a basic spaCy training configuration."""
    config_content = """[paths]
train = "./train.spacy"
dev = "./dev.spacy"
vectors = null
init_tok2vec = null

[system]
gpu_allocator = null
seed = 0

[nlp]
lang = "en"
pipeline = ["tok2vec", "ner"]
batch_size = 1000

[components]

[components.tok2vec]
factory = "tok2vec"

[components.tok2vec.model]
@architectures = "spacy.Tok2Vec.v2"

[components.tok2vec.model.embed]
@architectures = "spacy.MultiHashEmbed.v2"
width = 128
rows = [5000, 2000, 1000, 1000]
attrs = ["NORM", "PREFIX", "SUFFIX", "SHAPE"]
include_static_vectors = false

[components.tok2vec.model.encode]
@architectures = "spacy.MaxoutWindowEncoder.v2"
width = 128
window_size = 1
maxout_pieces = 3
depth = 4

[components.ner]
factory = "ner"

[components.ner.model]
@architectures = "spacy.TransitionBasedParser.v2"
state_type = "ner"
extra_state_tokens = false
hidden_width = 128
maxout_pieces = 3
use_upper = true
n_steps = 0
dropout = 0.1

[components.ner.model.tok2vec]
@architectures = "spacy.Tok2VecListener.v2"
width = 128

[corpora]

[corpora.train]
@readers = "spacy.Corpus.v0.2.2"
path = ${paths.train}
max_length = 0

[corpora.dev]
@readers = "spacy.Corpus.v0.2.2"
path = ${paths.dev}
max_length = 0

[training]
dev_corpus = "corpora.dev"
train_corpus = "corpora.train"

[training.batcher]
@schedules = "spacy.constant.v1"
value = 2000
tolerance = 0.2

[training.optimizer]
@optimizers = "Adam.v1"
beta1 = 0.9
beta2 = 0.999
L2_is_weight_decay = true
L2 = 0.01
grad_clip = 1.0
use_averages = false
eps = 0.00000001
learn_rate = 0.001

[training.optimizer.learn_rate]
@schedules = "spacy.linear.v1"
warmup_steps = 250
total_steps = 20000
initial_rate = 0.025
final_rate = 0.001

[training.score_weights]
ner_f = 1.0
ner_p = 0.0
ner_r = 0.0
"""
    
    with open("base_config.cfg", "w") as f:
        f.write(config_content)
    
    print("✅ Training configuration created: base_config.cfg")

def extract_structured_data(resume_text, model_path="./output/model-best"):
    """Extract structured data using trained model."""
    try:
        nlp_custom = spacy.load(model_path)
        doc = nlp_custom(resume_text)
        
        structured_output = {
            "name": None,
            "contact": {"email": [], "phone": []},
            "skills": [],
            "experience": [],
            "education": []
        }
        
        # Map entities to the structured dictionary
        for ent in doc.ents:
            if ent.label_ == "NAME":
                structured_output["name"] = ent.text
            elif ent.label_ == "EMAIL":
                structured_output["contact"]["email"].append(ent.text)
            elif ent.label_ == "PHONE":
                structured_output["contact"]["phone"].append(ent.text)
            elif ent.label_ == "SKILL":
                structured_output["skills"].append(ent.text)
            elif ent.label_ in ["JOB_TITLE", "ORG", "DATES", "DEGREE", "EDUCATION"]:
                structured_output["experience"].append((ent.label_, ent.text))
                 
        return structured_output
        
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        return {}

def main():
    """Main function to run the training pipeline."""
    print("🤖 Resume NER Model Training Pipeline")
    print("=" * 50)
    
    # Step 1: Generate training data from resumes
    print("\n1️⃣ Generating training data from resume dataset...")
    auto_training_data = generate_training_data_from_resumes()
    
    # Step 2: Combine with manual training data
    print("\n2️⃣ Combining with manual training data...")
    all_training_data = MANUAL_TRAIN_DATA + auto_training_data
    
    print(f"📊 Total training examples: {len(all_training_data)}")
    
    if len(all_training_data) < 5:
        print("❌ Not enough training data. Please add more examples.")
        return
    
    # Step 3: Train the model
    print("\n3️⃣ Training NER model...")
    success = train_ner_model(all_training_data)
    
    if success:
        print("\n✅ Training completed successfully!")
        print("\n📋 Next steps:")
        print("1. Test the model with: python3 test_resume_processing.py")
        print("2. Use the model for resume analysis")
        print("3. Fine-tune with more data if needed")
    else:
        print("\n❌ Training failed. Check the error messages above.")

if __name__ == "__main__":
    main()

