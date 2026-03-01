import os
import json
import requests

def analyze_candidate(skills, experience, projects):
    api_key = "AIzaSyB2WQ_gHjwFnxq8605dx5IwSpYEQ7bmA_Q"
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    prompt = f"""
    You are an AI Career Intelligence Engine. 
    
    Analyze the candidate profile below and calculate role match percentages for the following roles: 
    - Data Analyst 
    - Business Analyst 
    - Backend Developer 
    - DevOps Engineer 
    
    Candidate Profile: 
    Skills: {skills} 
    Experience: {experience} years 
    Projects: {projects} 
    
    For each role: 
    1. Calculate a realistic match percentage (0-100%). 
    2. List matched skills. 
    3. List missing critical skills. 
    4. Brief explanation (2 lines max). 
    
    Return output strictly in JSON format: 
    
    {{ 
      "roles": [ 
        {{ 
          "role": "", 
          "match_percentage": 0, 
          "matched_skills": [], 
          "missing_skills": [], 
          "reason": "" 
        }} 
      ] 
    }}
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        response = requests.post(f"{url}?key={api_key}", json=payload)
        response.raise_for_status()
        result = response.json()
        content = result['candidates'][0]['content']['parts'][0]['text'].strip()
        
        # Extract JSON from potential markdown
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        return json.loads(content)
    except Exception as e:
        return {"error": str(e)}

# Example data from user prompt placeholders
skills_list = "Python, SQL, AWS, Docker, Git, Tableau, Excel"
years_experience = "3"
project_summary = "Built a sales dashboard using Tableau and SQL; deployed a microservice using Docker on AWS EC2."

if __name__ == "__main__":
    analysis = analyze_candidate(skills_list, years_experience, project_summary)
    print(json.dumps(analysis, indent=2))
