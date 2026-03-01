import hashlib
from django.core.cache import cache

def get_resume_hash(resume_text, target_role):
    combined = f"{resume_text.strip().lower()}_{target_role.strip().lower()}"
    return hashlib.md5(combined.encode('utf-8')).hexdigest()

def get_cached_analysis(resume_text, target_role):
    key = f"analysis_{get_resume_hash(resume_text, target_role)}"
    return cache.get(key)

def set_cached_analysis(resume_text, target_role, data):
    key = f"analysis_{get_resume_hash(resume_text, target_role)}"
    cache.set(key, data, 60 * 60 * 24)
