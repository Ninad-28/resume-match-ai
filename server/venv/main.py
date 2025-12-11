import os
import json
import random
import time
import requests
import re
from fastapi import FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
import uvicorn
import google.generativeai as genai

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================================
# 🔑 YOUR GOOGLE GEMINI API KEY
# ==========================================================
GEMINI_API_KEY = "AIzaSyDQqMuSj6Sxmi1Nf0ZTOGJlAwnEppdWC2Q" 
# ==========================================================

# ADZUNA KEYS
ADZUNA_APP_ID = "62be064b"
ADZUNA_APP_KEY = "9d603bf16af924801ea9d05035b231b6"

# ==========================================================
# 🧠 LOCAL KNOWLEDGE BASE (THE FALLBACK BRAIN)
# ==========================================================

# 1. Master Skill List (For Regex Matching)
ALL_SKILLS_DB = {
    "python", "java", "c++", "c#", "javascript", "typescript", "react", "angular", "vue", "next.js",
    "node.js", "express", "django", "flask", "fastapi", "spring", "springboot", "dotnet",
    "sql", "mysql", "postgresql", "mongodb", "redis", "oracle", "nosql",
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "terraform", "ansible",
    "git", "github", "gitlab", "ci/cd", "devops",
    "machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch", "scikit-learn", "pandas",
    "html", "css", "tailwind", "bootstrap", "figma", "adobe xd",
    "linux", "bash", "shell", "jira", "agile", "scrum", "kanban",
    "networking", "tcp/ip", "dns", "firewall", "wireshark",
    "selenium", "junit", "pytest", "cypress", "manual testing", "automation testing",
    "tableau", "powerbi", "looker", "excel", "statistics", "probability"
}

# 2. Job Role Definitions (Skills, Improvements, Roadmap)
JOB_ROLES_DATA = {
    "software engineer": {
        "required": {"python", "java", "c++", "data structures", "algorithms", "sql", "git"},
        "roadmap": ["Week 1: Master DSA (LeetCode).", "Week 2: Build a full-stack project.", "Week 3: Learn System Design."],
        "tips": ["Highlight algorithmic problem solving.", "Showcase complex projects."]
    },
    "full-stack": {
        "required": {"javascript", "react", "node.js", "sql", "mongodb", "html", "css", "git"},
        "roadmap": ["Week 1: Build a MERN stack app.", "Week 2: Learn Docker & Deployment.", "Week 3: Add Authentication (OAuth)."],
        "tips": ["Link to your live portfolio.", "Mention both Frontend and Backend frameworks."]
    },
    "frontend": {
        "required": {"javascript", "react", "html", "css", "typescript", "redux", "tailwind"},
        "roadmap": ["Week 1: Master React Hooks.", "Week 2: Learn State Management (Redux).", "Week 3: Clone a popular UI (Netflix/Airbnb)."],
        "tips": ["Focus on UI/UX details.", "Ensure your projects are mobile responsive."]
    },
    "backend": {
        "required": {"python", "java", "node.js", "sql", "redis", "api", "docker"},
        "roadmap": ["Week 1: Build a REST API.", "Week 2: Learn Database Optimization.", "Week 3: Implement Caching (Redis)."],
        "tips": ["Highlight API performance.", "Discuss database schema design."]
    },
    "data scientist": {
        "required": {"python", "sql", "pandas", "numpy", "scikit-learn", "statistics", "machine learning"},
        "roadmap": ["Week 1: Exploratory Data Analysis (EDA).", "Week 2: Train ML Models.", "Week 3: Learn Model Deployment."],
        "tips": ["Showcase Kaggle competitions.", "Explain the business impact of your models."]
    },
    "ai engineer": {
        "required": {"python", "tensorflow", "pytorch", "deep learning", "nlp", "computer vision"},
        "roadmap": ["Week 1: Master Neural Networks.", "Week 2: Build a Transformer model.", "Week 3: Deploy AI on the cloud."],
        "tips": ["Mention research papers read.", "Showcase Generative AI projects."]
    },
    "data analyst": {
        "required": {"sql", "excel", "powerbi", "tableau", "python", "statistics"},
        "roadmap": ["Week 1: Master SQL Joins.", "Week 2: Build a Dashboard (PowerBI).", "Week 3: Learn Python for Data."],
        "tips": ["Focus on data storytelling.", "Quantify datasets you analyzed."]
    },
    "devops": {
        "required": {"aws", "docker", "kubernetes", "jenkins", "linux", "terraform", "ci/cd"},
        "roadmap": ["Week 1: Containerize apps with Docker.", "Week 2: Build CI/CD pipelines.", "Week 3: Manage Infrastructure as Code."],
        "tips": ["Highlight automation scripts.", "Mention cloud certifications."]
    },
    "cybersecurity": {
        "required": {"networking", "linux", "python", "firewall", "wireshark", "penetration testing"},
        "roadmap": ["Week 1: Network Security Basics.", "Week 2: Ethical Hacking Labs (Kali Linux).", "Week 3: Learn SOC analysis tools."],
        "tips": ["Show CTF (Capture The Flag) participation.", "Mention security certifications."]
    },
    "product manager": {
        "required": {"agile", "jira", "scrum", "roadmap", "strategy", "user research"},
        "roadmap": ["Week 1: Learn Agile Methodologies.", "Week 2: Write PRDs (Product Req Docs).", "Week 3: Conduct User Interviews."],
        "tips": ["Focus on 'Product Sense'.", "Highlight leadership experiences."]
    },
    "ui/ux": {
        "required": {"figma", "adobe xd", "prototyping", "wireframing", "user research"},
        "roadmap": ["Week 1: Master Figma Auto-layout.", "Week 2: Build a High-Fidelity Prototype.", "Week 3: Conduct Usability Testing."],
        "tips": ["Link to your Behance/Dribbble.", "Explain your design thinking process."]
    },
    "qa engineer": {
        "required": {"selenium", "java", "python", "manual testing", "jira", "sql"},
        "roadmap": ["Week 1: Learn Manual Testing concepts.", "Week 2: Write Selenium Automation scripts.", "Week 3: API Testing (Postman)."],
        "tips": ["Highlight bug tracking tools.", "Mention automation frameworks."]
    }
}

# --- HELPER FUNCTIONS ---
def extract_text_from_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def extract_skills_from_text(text):
    """Scans text for keywords in ALL_SKILLS_DB"""
    found = set()
    text = text.lower()
    for skill in ALL_SKILLS_DB:
        # Simple regex to match whole words (e.g. "C" won't match "Car")
        if re.search(r'\b' + re.escape(skill) + r'\b', text):
            found.add(skill)
    return found

# --- FALLBACK LOGIC ENGINE ---
def analyze_with_local_logic(resume_text, job_title):
    print(f"⚡ USING LOCAL LOGIC FOR: {job_title}")
    
    # 1. Identify Role
    job_key = "software engineer" # Default
    job_title_lower = job_title.lower()
    
    # Fuzzy match to find the closest role in our DB
    for key in JOB_ROLES_DATA:
        # e.g. match "Senior Full Stack Dev" to "full-stack"
        if key in job_title_lower or job_title_lower in key:
            job_key = key
            break
            
    role_data = JOB_ROLES_DATA.get(job_key, JOB_ROLES_DATA["software engineer"])
    required_skills = role_data["required"]
    
    # 2. Extract Skills from Resume
    my_skills = extract_skills_from_text(resume_text)
    
    # 3. Calculate Gap
    missing_skills = list(required_skills - my_skills)
    
    # 4. Calculate Score
    # Score = (Skills I Have / Skills Required) * 100
    matched_skills = required_skills.intersection(my_skills)
    if len(required_skills) > 0:
        score = int((len(matched_skills) / len(required_skills)) * 100)
    else:
        score = 50
        
    # Curve the score (Raw match is too harsh)
    score = min(score + 30, 95) # Add base points for experience
    
    # 5. Format Output
    return {
        "match_score": score,
        "missing_skills": missing_skills[:5], # Top 5 missing
        "improvements": role_data["tips"],
        "roadmap": role_data["roadmap"]
    }

# --- API ENDPOINTS ---

@app.get("/")
def home():
    return {"status": "Gemini + Local Logic Brain Active 🧠"}

@app.post("/search-jobs")
def find_jobs(role: str = Form(...), location: str = Form(""), company: str = Form("")):
    results = []
    if ADZUNA_APP_ID and ADZUNA_APP_KEY:
        try:
            url = f"https://api.adzuna.com/v1/api/jobs/in/search/1"
            params = {
                "app_id": ADZUNA_APP_ID, 
                "app_key": ADZUNA_APP_KEY, 
                "what": f"{role} {company}", 
                "where": location, 
                "results_per_page": 10, 
                "content-type": "application/json"
            }
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                for item in data.get('results', []):
                    results.append({
                        "id": str(item.get('id')),
                        "title": item.get('title').replace("<strong>", "").replace("</strong>", ""),
                        "source": "Adzuna",
                        "link": item.get('redirect_url'),
                        "snippet": item.get('description')[:200] + "..."
                    })
        except Exception:
            pass
            
    # Fallback to Demo Jobs if API fails
    if not results:
        role_cap = role.title()
        results = [
            { "id": "demo_1", "title": f"Senior {role_cap} Developer", "source": "LinkedIn", "link": "#", "snippet": "Demo..." },
            { "id": "demo_2", "title": f"{role_cap} Engineer", "source": "Naukri", "link": "#", "snippet": "Demo..." }
        ]
    return {"jobs": results}

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return {"filename": file_path, "message": "File uploaded"}

@app.post("/analyze-match")
async def analyze_match(filename: str = Form(...), job_title: str = Form(...), job_desc: str = Form(...)):
    print(f"\n🧠 ANALYZING: {job_title}")
    
    # 1. Read Resume
    if not os.path.exists(filename):
        return analyze_with_local_logic("", job_title)
    
    resume_text = extract_text_from_pdf(filename)

    # 2. TRY AI (PLAN A)
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Try a robust list of models
        model_options = ['gemini-2.0-flash-lite-preview-02-05', 'gemini-flash-lite-latest', 'gemini-1.5-flash']
        response = None

        for model_name in model_options:
            try:
                print(f"⏳ Trying AI model: {model_name}...")
                model = genai.GenerativeModel(model_name)
                
                prompt = f"""
                Act as an ATS. Compare Resume to Job.
                RESUME: {resume_text[:4000]}
                JOB TITLE: {job_title}
                JOB DESC: {job_desc}
                
                Return raw JSON:
                {{
                    "match_score": 0,
                    "missing_skills": ["Skill1", "Skill2"],
                    "improvements": ["Tip1", "Tip2"],
                    "roadmap": ["Step1", "Step2"]
                }}
                """
                
                response = model.generate_content(prompt)
                print(f"✅ AI Success!")
                break 
            except Exception:
                continue 

        if response:
            clean_text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)

    except Exception as e:
        print(f"❌ AI Failed: {e}")

    # 3. USE LOCAL LOGIC (PLAN B)
    # If we are here, AI failed or rate limited. Use Python logic.
    return analyze_with_local_logic(resume_text, job_title)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 