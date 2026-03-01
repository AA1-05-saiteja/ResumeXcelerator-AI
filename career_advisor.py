import json
import requests

def get_career_advice(skills, role, missing, current_score):
    api_key = "AIzaSyB2WQ_gHjwFnxq8605dx5IwSpYEQ7bmA_Q"
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    prompt = f"""
    You are an AI Career Growth Advisor. 
    
    Given the candidate profile and role match analysis below, suggest specific improvements. 
    
    Candidate Skills: 
    {skills} 
    
    Target Role: 
    {role} 
    
    Missing Skills: 
    {missing} 
    
    Current Match Score: 
    {current_score}% 
    
    Tasks: 
    1. Suggest top 3 high-impact skills to learn. 
    2. Suggest 1 practical project to add. 
    3. Estimate new match percentage if skills are learned. 
    4. Keep suggestions practical and realistic. 
    
    Return strictly in JSON: 
    
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

# Mock data for advisor logic demonstration
skills_list = "Python, Django, PostgreSQL, Git, AWS"
role_name = "Senior Backend Developer"
missing_skills = "Redis, Kubernetes, System Design"
current_score = 75

if __name__ == "__main__":
    advice = get_career_advice(skills_list, role_name, missing_skills, current_score)
    print(json.dumps(advice, indent=2))
