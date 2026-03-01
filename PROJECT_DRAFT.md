# ResumeXcelerater_AI – LLM-Based Prototype Draft

## 🎯 Objective

Build an AI-powered Resume Analyzer using Django + LLM.

The system should:
- Accept resume PDF upload
- Extract text
- Send resume + target role to LLM
- Receive structured JSON analysis
- Return result to frontend

No ML training. No datasets. LLM handles intelligence.

---

## 🏗 Architecture

User  
↓  
NGINX (amd.merzol.com)  
↓  
Gunicorn (127.0.0.1:9090)  
↓  
Django Backend  
↓  
LLM API (OpenAI or Local GPU)  

---

## 📂 Project Structure

amd/
│
├── core/
│
├── resume/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   ├── services/
│   │     ├── pdf_parser.py
│   │     └── llm_engine.py
│
├── media/
├── staticfiles/
└── db.sqlite3

---

## 🔹 API Design

### POST /api/analyze-resume/

### Input (multipart/form-data)
- resume_file (PDF)
- target_role (string)

---

## 🔹 Processing Flow

1. Save uploaded PDF
2. Extract text using PyMuPDF
3. Send prompt to LLM
4. Get structured JSON response
5. Save result in database
6. Return JSON response

---

## 🔹 LLM Prompt Template

You are an AI Resume Analyzer.

Analyze the following resume for the role: {target_role}

Return strictly valid JSON with:

- extracted_skills (list)
- matched_skills (list)
- missing_skills (list)
- match_percentage (0-100 number)
- readiness_score (0-100 number)
- roadmap (list of 5 improvement suggestions)

Resume Text:
{resume_text}

---

## 🔹 Expected JSON Output

{
  "extracted_skills": [],
  "matched_skills": [],
  "missing_skills": [],
  "match_percentage": 0,
  "readiness_score": 0,
  "roadmap": []
}

---

## 🔹 Database Model: ResumeAnalysis

Fields:
- id
- resume_file
- target_role
- extracted_skills (JSONField)
- matched_skills (JSONField)
- missing_skills (JSONField)
- match_percentage (FloatField)
- readiness_score (FloatField)
- roadmap (JSONField)
- created_at (auto_now_add)

---

## 🔹 Security Rules

- Max upload size: 10MB
- Only allow PDF
- Validate LLM JSON response
- If invalid JSON → return error
- Use environment variable for OPENAI_API_KEY

---

## 🔹 Phase 1 Deliverable

Working endpoint:
POST /api/analyze-resume/

Returns structured JSON from LLM.

END OF DOCUMENT