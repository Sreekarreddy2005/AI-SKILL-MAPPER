# In intelligence/scoring.py

from typing import List, Dict, Set

def calculate_weighted_score(job_skills: List[Dict], resume_skills: Set[str]) -> Dict:
    """
    Calculates a weighted match score based on skill types.

    Args:
        job_skills: A list of skill dictionaries from the parsed job description.
                    Each dict is expected to have 'skill_name' and 'type'.
        resume_skills: A normalized set of skill strings from the resume.

    Returns:
        A dictionary containing the detailed scoring results.
    """
    # Define the importance (weight) of each skill type
    skill_weights = {"technical": 3, "soft": 1} # 'tool' could be added later

    if not job_skills:
        return {
            "match_percentage": 0,
            "summary": "No required skills were identified in the job description.",
            "details": {
                "achieved_score": 0,
                "max_possible_score": 0,
                "matching_skills": [],
                "missing_skills": []
            }
        }

    achieved_score = 0
    max_possible_score = 0
    matching_skills = []
    missing_skills = []

    # Use a set for fast lookups
    job_skill_names_normalized = {skill['skill_name'] for skill in job_skills}

    # Identify matching and missing skills first
    matching_skill_names = job_skill_names_normalized.intersection(resume_skills)
    missing_skill_names = job_skill_names_normalized.difference(resume_skills)

    # Calculate scores based on the weights
    for skill in job_skills:
        skill_name = skill.get("skill_name")
        skill_type = skill.get("type", "technical") # Default to technical if type is missing
        weight = skill_weights.get(skill_type, 1)

        max_possible_score += weight

        if skill_name in matching_skill_names:
            achieved_score += weight
            matching_skills.append({"skill": skill_name, "type": skill_type})
        else:
            missing_skills.append({"skill": skill_name, "type": skill_type})

    match_percentage = (achieved_score / max_possible_score) * 100 if max_possible_score > 0 else 0

    summary = f"The candidate's skills align with {round(match_percentage, 2)}% of the job's weighted requirements."

    return {
        "match_percentage": round(match_percentage, 2),
        "summary": summary,
        "details": {
            "achieved_score": achieved_score,
            "max_possible_score": max_possible_score,
            "matching_skills": sorted(matching_skills, key=lambda x: x['skill']),
            "missing_skills": sorted(missing_skills, key=lambda x: x['skill'])
        }
    }
