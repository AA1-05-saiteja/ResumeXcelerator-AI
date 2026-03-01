import json
import os
import requests
import logging
import hashlib
from jsonschema import validate, ValidationError
from django.conf import settings
from .scoring import calculate_deterministic_score, calculate_confidence_score, get_or_create_role_profile, get_market_benchmark

logger = logging.getLogger(__name__)

RESUME_ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "extracted_skills": {"type": "array", "items": {"type": "string"}},
        "matched_skills": {"type": "array", "items": {"type": "string"}},
        "missing_skills": {"type": "array", "items": {"type": "string"}},
        "match_percentage": {"type": "number", "minimum": 0, "maximum": 100},
        "readiness_score": {"type": "number", "minimum": 0, "maximum": 100},
        "roadmap": {
            "type": "object",
            "properties": {
                "short_term": {"type": "array", "items": {"type": "string"}},
                "long_term": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["short_term", "long_term"]
        }
    },
    "required": [
        "extracted_skills", "matched_skills", "missing_skills",
        "match_percentage", "readiness_score", "roadmap"
    ]
}

def generate_resume_embedding(resume_text):
    return [ord(c) / 255.0 for c in hashlib.md5(resume_text.encode()).hexdigest()[:16]]

import time

def evaluate_fit_with_guardrails(resume_text, target_role, benchmark):
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    urls = [
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    ]
    
    prompt = f"""
    You are an AI Career Fit Evaluator. 
    
    Candidate Resume: 
    {resume_text} 
    
    Role Requirements (Market Benchmark): 
    {json.dumps(benchmark)}
    
    Tasks: 
    1. Evaluate skill alignment realistically. 
    2. Consider depth, not just keyword matching. 
    3. Assign a match percentage (0-100%). 
    4. Give 2-line professional reasoning. 
    
    Scoring Rules:
    - 90%+ only if candidate satisfies most advanced skills
    - 70–85% for strong mid-level alignment
    - 50–70% for partial alignment
    - Below 50% if core gaps exist
    - Never give 95%+ unless nearly perfect match
    
    Return output strictly in JSON format. 
    IMPORTANT: "extracted_skills", "matched_skills", and "missing_skills" MUST be arrays of simple strings, NOT objects.
    
    {{ 
      "extracted_skills": ["Skill 1", "Skill 2"],
      "matched_skills": ["Skill 1"],
      "missing_skills": ["Skill 3"],
      "match_percentage": 0,
      "readiness_score": 0,
      "reason": "",
      "roadmap": {{"short_term": ["Action 1"], "long_term": ["Action 2"]}}
    }}
    """
    
    response = None
    for url in urls:
        for attempt in range(2):
            try:
                # Append key to URL
                api_url = f"{url}?key={api_key}"
                # Reduced timeout to 30s to stay within Gunicorn limits
                r = requests.post(api_url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30)
                if r.status_code == 200:
                    response = r
                    break
                elif r.status_code == 429:
                    logger.warning(f"Rate limited on {url}, retrying...")
                    time.sleep(2)
                    continue
                else:
                    logger.error(f"API Error {r.status_code} on {url}: {r.text}")
                    break
            except Exception as e:
                logger.error(f"Connection error on {url}: {e}")
                break
        if response: break

    if not response:
        return None
        
    try:
        data = response.json()
        content = data['candidates'][0]['content']['parts'][0]['text'].strip()
        start = content.find("{")
        end = content.rfind("}")
        result = json.loads(content[start:end+1])
        validate(instance=result, schema=RESUME_ANALYSIS_SCHEMA)
        return result
    except Exception as e:
        logger.error(f"Fit evaluation parsing failed: {e}")
        return None

def simulate_growth_with_rules(role, current_score, missing_skills, profile_summary):
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    urls = [
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    ]
    
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
    
    Stability Rules:
    - future_match_percentage <= 95 
    - future_match_percentage >= current_score + 5 
    - Do not increase more than 20% from current match. 
    
    Return output strictly in JSON format.
    IMPORTANT: "skills_to_learn" MUST be an array of simple strings, NOT objects.
    
    {{ 
      "skills_to_learn": ["Skill 1", "Skill 2"], 
      "project_suggestion": "", 
      "future_match_percentage": 0 
    }}
    """
    
    response = None
    for url in urls:
        for attempt in range(2):
            try:
                # Append key to URL
                api_url = f"{url}?key={api_key}"
                # Reduced timeout to 30s to stay within Gunicorn limits
                r = requests.post(api_url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30)
                if r.status_code == 200:
                    response = r
                    break
                elif r.status_code == 429:
                    logger.warning(f"Rate limited on {url}, retrying...")
                    time.sleep(2)
                    continue
                else:
                    logger.error(f"API Error {r.status_code} on {url}: {r.text}")
                    break
            except Exception as e:
                logger.error(f"Connection error on {url}: {e}")
                break
        if response: break

    if not response:
        return None
        
    try:
        data = response.json()
        content = data['candidates'][0]['content']['parts'][0]['text'].strip()
        start = content.find("{")
        end = content.rfind("}")
        return json.loads(content[start:end+1])
    except Exception as e:
        logger.error(f"Growth simulation parsing failed: {e}")
        return None

def generate_career_dashboard_summary(target_role, fit_data, growth_data):
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    urls = [
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    ]
    
    # Static salary mapping for demo (Tier-1 India)
    salary_tiers = {
        "Data Analyst": "₹8L - ₹18L",
        "Business Analyst": "₹10L - ₹22L",
        "Backend Developer": "₹12L - ₹35L",
        "DevOps Engineer": "₹14L - ₹40L"
    }
    salary_range = salary_tiers.get(target_role, "₹10L - ₹25L")

    prompt = f"""
    You are an AI Career Coach. 
    Generate an executive-level Career Intelligence Dashboard summary.
    
    Inputs:
    - Target Role: {target_role}
    - Current Match: {fit_data['match_percentage']}%
    - Future Match: {growth_data['future_match_percentage']}%
    - Salary Insight: {salary_range}
    - Strengths: {fit_data['matched_skills'][:3]}
    - Roadmap Steps: {growth_data['skills_to_learn']}
    
    Tasks: 
    1. Create a professional, concise executive summary.
    2. Do NOT recalculate scores. Use provided inputs.
    
    Return output strictly in JSON format.
    IMPORTANT: "top_roles" and "growth_roadmap" MUST be arrays of simple strings, NOT objects.
    
    {{ 
      "executive_summary": "",
      "top_roles": ["{target_role}", "Secondary Role"],
      "salary_insight": "{salary_range}",
      "growth_roadmap": ["Action 1", "Action 2"]
    }}
    """
    
    response = None
    for url in urls:
        for attempt in range(2):
            try:
                # Append key to URL
                api_url = f"{url}?key={api_key}"
                # Reduced timeout to 30s to stay within Gunicorn limits
                r = requests.post(api_url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30)
                if r.status_code == 200:
                    response = r
                    break
                elif r.status_code == 429:
                    logger.warning(f"Rate limited on {url}, retrying...")
                    time.sleep(2)
                    continue
                else:
                    logger.error(f"API Error {r.status_code} on {url}: {r.text}")
                    break
            except Exception as e:
                logger.error(f"Connection error on {url}: {e}")
                break
        if response: break

    if not response:
        return None
        
    try:
        data = response.json()
        content = data['candidates'][0]['content']['parts'][0]['text'].strip()
        start = content.find("{")
        end = content.rfind("}")
        return json.loads(content[start:end+1])
    except Exception as e:
        logger.error(f"Dashboard summary parsing failed: {e}")
        return None

def analyze_resume_with_llm(resume_text, target_role):
    benchmark = get_market_benchmark(target_role)
    if not benchmark:
        raise ValueError("Could not establish market benchmark for role")

    fit_data = evaluate_fit_with_guardrails(resume_text, target_role, benchmark)
    if not fit_data:
        raise ValueError("Failed to evaluate candidate fit")
        
    growth_data = simulate_growth_with_rules(
        target_role, 
        fit_data['match_percentage'], 
        fit_data['missing_skills'], 
        resume_text[:1000]
    )
    
    if not growth_data:
        raise ValueError("Failed to simulate growth trajectory")
        
    dashboard_summary = generate_career_dashboard_summary(target_role, fit_data, growth_data)
    
    final_result = {
        **fit_data,
        "improvement_plan": growth_data,
        "dashboard_summary": dashboard_summary,
        "confidence_score": calculate_confidence_score(fit_data['match_percentage']),
        "resume_embedding": generate_resume_embedding(resume_text),
        "role_profile_version": benchmark.get('version', 'v1.0')
    }
    
    return final_result
