import json
import logging
import requests
from django.conf import settings
from .models import RoleSkill, RoleMarketBenchmark
from django.utils import timezone

logger = logging.getLogger(__name__)

def get_market_benchmark(role_name):
    role_name_clean = role_name.strip().title()
    benchmark = RoleMarketBenchmark.objects.filter(role=role_name_clean).first()
    
    one_week_ago = timezone.now() - timezone.timedelta(days=7)
    
    if benchmark and benchmark.created_at > one_week_ago:
        return {
            "core_skills": benchmark.core_skills,
            "advanced_skills": benchmark.advanced_skills,
            "experience_expectation": benchmark.experience_expectation,
            "project_expectation": benchmark.project_expectation,
            "version": benchmark.version
        }
    
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    # Using Gemini 2.5 Flash as requested
    api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    
    prompt = f"""
    You are an AI Career Intelligence Engine. 
    Define the realistic required skill structure for the role: "{role_name_clean}"
    Based on current Indian tech market standards.
    
    Return output strictly in JSON format: 
    {{ 
      "core_skills": [], 
      "advanced_skills": [], 
      "experience_expectation": "", 
      "project_expectation": "" 
    }}
    """
    
    try:
        response = requests.post(f"{api_url}?key={api_key}", json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30)
        
        if response.status_code != 200:
            # Fallback to 1.5
            api_url_alt = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
            response = requests.post(f"{api_url_alt}?key={api_key}", json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30)
            response.raise_for_status()
            
        data = response.json()
        content = data['candidates'][0]['content']['parts'][0]['text'].strip()
        
        start = content.find("{")
        end = content.rfind("}")
        result = json.loads(content[start:end+1])
        
        new_version = "v1.0"
        if benchmark:
            v_num = float(benchmark.version.replace('v', ''))
            new_version = f"v{round(v_num + 0.1, 1)}"
            benchmark.core_skills = result['core_skills']
            benchmark.advanced_skills = result['advanced_skills']
            benchmark.experience_expectation = result['experience_expectation']
            benchmark.project_expectation = result['project_expectation']
            benchmark.version = new_version
            benchmark.save()
        else:
            RoleMarketBenchmark.objects.create(
                role=role_name_clean,
                core_skills=result['core_skills'],
                advanced_skills=result['advanced_skills'],
                experience_expectation=result['experience_expectation'],
                project_expectation=result['project_expectation'],
                version=new_version
            )
            
        return result
    except Exception as e:
        logger.error(f"Failed to generate market benchmark: {e}")
        return None

def generate_role_profile(role_name):
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    if not api_key:
        raise ValueError("Gemini API key missing")

    api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    
    prompt = f"""
    Create a professional skill profile for the role: "{role_name}"
    Return ONLY a JSON object with a single key "skills" containing a list of exactly 10 most critical technical and soft skills.
    """

    try:
        response = requests.post(f"{api_url}?key={api_key}", json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30)
        if response.status_code != 200:
            api_url_alt = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
            response = requests.post(f"{api_url_alt}?key={api_key}", json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30)
            response.raise_for_status()
            
        data = response.json()
        content = data['candidates'][0]['content']['parts'][0]['text'].strip()
        start = content.find("{")
        end = content.rfind("}")
        profile = json.loads(content[start:end+1])
        return profile.get("skills", [])
    except Exception as e:
        logger.error(f"Profile generation failed: {e}")
        return []

def get_or_create_role_profile(role_name):
    role_name_clean = role_name.strip().title()
    profile, created = RoleSkill.objects.get_or_create(role_name=role_name_clean)
    if created or not profile.is_locked or not profile.required_skills:
        skills = generate_role_profile(role_name_clean)
        if skills:
            profile.required_skills = skills
            profile.is_locked = True
            profile.version += 1
            profile.save()
    return profile

def calculate_deterministic_score(extracted_skills, role_profile):
    required = set(s.lower() for s in role_profile.required_skills)
    if not required: return 0.0, []
    extracted = set(s.lower() for s in extracted_skills)
    matched = required.intersection(extracted)
    percentage = (len(matched) / len(required)) * 100
    return round(percentage, 2), list(matched)

def calculate_confidence_score(match_percentage):
    base = 0.90
    if match_percentage > 80: base += 0.05
    if match_percentage < 20: base -= 0.15
    return round(min(base, 1.0), 2)
