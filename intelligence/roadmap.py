import json
from typing import List, Dict, Set
from .resource_finder import find_youtube_resources

# --- Configuration Data ---

# Defines which skills should be learned before others
SKILL_DEPENDENCIES = {
    "React": ["JavaScript"],
    "Spring Boot": ["Java", "SQL"],
    "Machine Learning": ["Python"],
    "Deep Learning": ["Machine Learning", "Python"],
    "Data Visualization": ["SQL"],
    "Tableau": ["Data Visualization"],
    "PowerBI": ["Data Visualization"]
}

# Estimates learning time for each skill
SKILL_TIMELINES = {
    "default": {"weeks": 4, "difficulty": "Intermediate"},
    "Python": {"weeks": 5, "difficulty": "Beginner"},
    "SQL": {"weeks": 3, "difficulty": "Beginner"},
    "JavaScript": {"weeks": 4, "difficulty": "Beginner"},
    "Java": {"weeks": 6, "difficulty": "Beginner"},
    "React": {"weeks": 5, "difficulty": "Intermediate"},
    "Machine Learning": {"weeks": 8, "difficulty": "Advanced"},
    "Deep Learning": {"weeks": 10, "difficulty": "Advanced"},
    "Data Visualization": {"weeks": 2, "difficulty": "Beginner"}
}

# --- Resource Loading ---

def load_resources() -> Dict:
    """Loads learning resources from the JSON file."""
    try:
        with open('resources.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Warning: resources.json not found. No local resources will be used.")
        return {}
    except json.JSONDecodeError:
        print("Warning: Could not decode resources.json. File might be empty or malformed.")
        return {}

RESOURCES = load_resources()

# --- Core Roadmap Logic ---

def generate_learning_roadmap(missing_skills: List[str], existing_skills: Set[str]) -> List[Dict]:
    """
    Generates a sorted, time-estimated learning roadmap with resources.
    It uses a hybrid approach: curated JSON file first, then YouTube API as a fallback.
    """
    if not missing_skills:
        return []

    # Step 1: Determine the full set of skills to learn, including prerequisites
    skills_to_learn = set(missing_skills)
    for skill in list(skills_to_learn): # Use a copy to modify the set during iteration
        dependencies = SKILL_DEPENDENCIES.get(skill, [])
        for dep in dependencies:
            if dep not in existing_skills and dep not in skills_to_learn:
                skills_to_learn.add(dep)

    # Step 2: Sort the skills based on dependencies (a simplified topological sort)
    sorted_roadmap_skills = []
    learning_queue = list(skills_to_learn)
    
    # Loop to ensure all dependencies are met before adding a skill
    iterations = 0
    max_iterations = len(learning_queue) + 5 # Safety break for circular dependencies
    while learning_queue and iterations < max_iterations:
        skill_added_in_pass = False
        remaining_skills = []
        
        for skill in learning_queue:
            dependencies = SKILL_DEPENDENCIES.get(skill, [])
            if all(dep in existing_skills or dep in sorted_roadmap_skills for dep in dependencies):
                sorted_roadmap_skills.append(skill)
                skill_added_in_pass = True
            else:
                remaining_skills.append(skill)
        
        if not skill_added_in_pass and remaining_skills:
            # If a pass completes with no skills added, there might be a circular dependency.
            # For robustness, add the rest without strict ordering to prevent an infinite loop.
            sorted_roadmap_skills.extend(remaining_skills)
            break
            
        learning_queue = remaining_skills
        iterations += 1

    # Step 3: Build the final roadmap structure with timelines and resources
    final_roadmap = []
    total_weeks = 0
    for i, skill_name in enumerate(sorted_roadmap_skills):
        # First, try to get resources from our curated JSON file
        resources = RESOURCES.get(skill_name)
        
        # If no local resources are found, call the YouTube API
        if not resources:
            print(f"No local resources for '{skill_name}'. Fetching from YouTube...")
            resources = find_youtube_resources(skill_name)
        
        timeline = SKILL_TIMELINES.get(skill_name, SKILL_TIMELINES["default"])
        
        cumulative_weeks = total_weeks + timeline["weeks"]
        
        final_roadmap.append({
            "step": i + 1,
            "skill": skill_name,
            "estimated_weeks": timeline["weeks"],
            "difficulty": timeline["difficulty"],
            "cumulative_weeks": cumulative_weeks,
            "resources": resources
        })
        
        total_weeks = cumulative_weeks

    return final_roadmap