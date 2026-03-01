import json
import requests
import os

def evaluate_fit():
    api_key = "AIzaSyB2WQ_gHjwFnxq8605dx5IwSpYEQ7bmA_Q"
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    # Context from previous turns
    candidate_profile = {
        "skills": "Python, SQL, AWS, Docker, Git, Tableau, Excel",
        "years": "3",
        "projects": "Built a sales dashboard using Tableau and SQL; deployed a microservice using Docker on AWS EC2."
    }
    
    role_definition = {
        "role": "Backend Developer",
        "core_skills": ["Python (Django/FastAPI) or Java (Spring Boot)", "RESTful APIs", "SQL (PostgreSQL/MySQL)", "Git", "Data Structures & Algorithms"],
        "advanced_skills": ["Redis/Caching", "Message Queues (Kafka/RabbitMQ)", "Microservices Architecture", "System Design (HLD/LLD)"],
        "experience_expectation": "2-6 years; focus on high-scale distributed systems.",
        "project_expectation": "Developing scalable API services handling 10k+ RPM; implementing complex third-party integrations (Payments/Auth)."
    }

    prompt = f"""
    You are an AI Career Fit Evaluator. 
    
    Candidate Profile: 
    Skills: {candidate_profile['skills']} 
    Experience: {candidate_profile['years']} years
    Projects: {candidate_profile['projects']} 
    
    Role Requirements: 
    {json.dumps(role_definition)}
    
    Tasks: 
    1. Evaluate skill alignment realistically. 
    2. Consider depth, not just keyword matching. 
    3. Assign a match percentage (0-100%). 
    4. List matched strengths. 
    5. List missing high-impact skills. 
    6. Give 2-line professional reasoning. 
    
    Return output strictly in JSON format: 
    {{ 
      "role": "{role_definition['role']}", 
      "match_percentage": 0, 
      "strengths": [], 
      "missing_skills": [], 
      "reason": "" 
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
        
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        return json.loads(content)
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    evaluation = evaluate_fit()
    print(json.dumps(evaluation, indent=2))
