#!/usr/bin/env python3
"""
Quick test script to debug the search functionality
"""
import json
from pathlib import Path

def test_search():
    # Load data
    DATA_PATH = Path("dataset/employees.json")
    with open(DATA_PATH) as f:
        DATA = json.load(f)["employees"]
    
    query = "I need someone experienced with machine learning for a healthcare project"
    q = query.lower()
    
    print(f"🔍 Testing query: '{query}'")
    print(f"🔍 Lowercase: '{q}'")
    print(f"📊 Total employees: {len(DATA)}")
    
    # Test the search logic
    candidates = []
    
    for i, e in enumerate(DATA):
        score = 0
        matches = []
        
        # Check for ML/Machine Learning keywords
        ml_keywords = ['ml', 'machine learning', 'tensorflow', 'pytorch', 'scikit-learn', 'sklearn', 'pandas']
        for keyword in ml_keywords:
            if keyword in q:
                for skill in e["skills"]:
                    if keyword.lower() in skill.lower() or skill.lower() in ['ml', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas']:
                        score += 3
                        matches.append(f"ML: {skill}")
        
        # Check for healthcare keywords
        healthcare_keywords = ['healthcare', 'medical', 'health', 'patient', 'clinical', 'diagnosis', 'hipaa']
        for keyword in healthcare_keywords:
            if keyword in q:
                for project in e["projects"]:
                    if keyword.lower() in project.lower() or any(hw in project.lower() for hw in healthcare_keywords):
                        score += 2
                        matches.append(f"Healthcare Project: {project}")
                for skill in e["skills"]:
                    if keyword.lower() in skill.lower():
                        score += 2
                        matches.append(f"Healthcare Skill: {skill}")
        
        if score > 0:
            candidates.append((score, e, matches))
            print(f"✅ {e['name']} (ID: {e['id']}) - Score: {score}")
            for match in matches:
                print(f"   📌 {match}")
            print()
    
    print(f"📈 Total candidates found: {len(candidates)}")
    
    if candidates:
        candidates.sort(key=lambda x: (-x[0], -x[1]["experience_years"]))
        print("\n🎯 Top candidates:")
        for i, (score, emp, matches) in enumerate(candidates[:5], 1):
            print(f"{i}. {emp['name']} (Score: {score}, Experience: {emp['experience_years']} years)")
    else:
        print("❌ No candidates found!")

if __name__ == "__main__":
    test_search()
