import json
import requests
import os

def generate_market_benchmarks():
    api_key = "AIzaSyB2WQ_gHjwFnxq8605dx5IwSpYEQ7bmA_Q"
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    prompt = """
    You are an AI Career Intelligence Engine trained on real-world hiring trends in India. 
    
    Task: 
    Based on current Indian tech market standards (Tier-1 and Product-based companies), define the realistic required skill structure for:
    - Data Analyst 
    - Business Analyst 
    - Backend Developer 
    - DevOps Engineer 
    
    For each role: 
    1. Define core skills (must-have) 
    2. Define advanced skills (high-impact) 
    3. Define experience expectations (brief) 
    4. Define typical project expectations 
    
    Return output strictly in JSON format: 
    { 
      "roles": [ 
        { 
          "role": "", 
          "core_skills": [], 
          "advanced_skills": [], 
          "experience_expectation": "", 
          "project_expectation": "" 
        } 
      ] 
    }
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
    benchmarks = generate_market_benchmarks()
    print(json.dumps(benchmarks, indent=2))
