import os
import requests
import logging

logger = logging.getLogger(__name__)

def fetch_live_jobs(role: str, location: str = "India") -> list:
    app_id = os.getenv("ADZUNA_APP_ID")
    app_key = os.getenv("ADZUNA_APP_KEY")
    
    if not app_id or not app_key:
        logger.error("Adzuna API credentials missing in environment variables.")
        return []

    base_url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
    
    params = {
        "app_id": app_id,
        "app_key": app_key,
        "what": role,
        "where": location,
        "results_per_page": 5,
        "content-type": "application/json"
    }

    try:
        response = requests.get(base_url, params=params, timeout=10)
        
        if response.status_code != 200:
            logger.error(f"Adzuna API returned status code {response.status_code}")
            return []
            
        data = response.json()
        results = data.get("results", [])
        
        structured_jobs = []
        for job in results:
            structured_jobs.append({
                "title": job.get("title", "").replace("<strong>", "").replace("</strong>", ""),
                "company": job.get("company", {}).get("display_name", ""),
                "location": job.get("location", {}).get("display_name", ""),
                "salary_min": job.get("salary_min"),
                "salary_max": job.get("salary_max"),
                "redirect_url": job.get("redirect_url", ""),
                "description": job.get("description", "").replace("<strong>", "").replace("</strong>", "")[:150] + "..."
            })
            
        return structured_jobs

    except Exception as e:
        logger.error(f"Error fetching jobs from Adzuna: {str(e)}")
        return []
