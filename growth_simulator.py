import json
import requests
import os

def simulate_growth():
    api_key = "AIzaSyB2WQ_gHjwFnxq8605dx5IwSpYEQ7bmA_Q"
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    # Context from previous evaluations
    role = "Backend Developer"
    current_score = 78
    missing_skills = ["Redis/Caching", "Message Queues (Kafka/RabbitMQ)", "Advanced System Design (HLD/LLD)", "Unit Testing Frameworks"]
    profile_summary = "3 years experience with Python, SQL, AWS, and Docker. Successfully deployed microservices on EC2."

    prompt = f"""
    You are an AI Career Growth Simulator. 
    
    Given: 
    Role: {role} 
    Current Match Score: {current_score}% 
    Missing Skills: {missing_skills} 
    Candidate Background: {profile_summary} 
    
    Tasks: 
    1. Identify top 3 most impactful skills to learn. 
    2. Suggest one advanced real-world project. 
    3. Estimate realistic future match percentage after mastering these. 
    4. Do NOT exceed 95% unless candidate is near-perfect. 
    
    Return output strictly in JSON format: 
    {{ 
      "role": "{role}", 
      "improvement_plan": {{ 
        "skills_to_learn": [], 
        "project_suggestion": "", 
        "future_match_percentage": 0 
      }} 
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
    simulation = simulate_growth()
    print(json.dumps(simulation, indent=2))
