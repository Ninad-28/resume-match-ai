import os
import json
import random
import time
import requests  # Needed for Adzuna API
from fastapi import FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
import uvicorn
from openai import OpenAI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 1. CONFIGURATION ---

# OPENAI KEY (Optional: Leave empty for Mock AI Mode)
OPENAI_API_KEY = ""  
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# ADZUNA API KEYS (Real Data)
ADZUNA_APP_ID = "62be064b"
ADZUNA_APP_KEY = "9d603bf16af924801ea9d05035b231b6"

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

def generate_mock_analysis():
    """Fallback logic if OpenAI is not available"""
    score = random.randint(65, 88)
    return {
        "match_score": score,
        "missing_skills": ["Docker", "Kubernetes", "System Design", "GraphQL"],
        "improvements": [
            "Use stronger action verbs like 'Architected' or 'Deployed'.",
            "Quantify your results (e.g., 'Reduced latency by 40%').",
            "Add a 'Technical Skills' section at the top."
        ],
        "roadmap": [
            "Week 1: Master Docker & Containerization concepts.",
            "Week 2: Build a microservice project using GraphQL.",
            "Week 3: Practice System Design problems on LeetCode."
        ]
    }

def get_demo_jobs(role, location):
    """Fallback generator for high-quality demo data if API fails"""
    print("⚠️ Using Demo Data (API limit reached or error)")
    role_cap = role.title()
    linkedin_url = f"https://www.linkedin.com/jobs/search/?keywords={role}&location={location}"
    
    return [
        {
            "id": "demo_1",
            "title": f"Senior {role_cap} Developer",
            "source": "LinkedIn",
            "link": linkedin_url,
            "snippet": f"We are looking for an experienced {role_cap} with strong skills in scalable systems..."
        },
        {
            "id": "demo_2",
            "title": f"{role_cap} Engineer - High Growth Startup",
            "source": "Naukri",
            "link": f"https://www.naukri.com/{role}-jobs-in-{location}",
            "snippet": f"Urgent hiring for {role_cap}. 3+ years experience required."
        },
        {
            "id": "demo_3",
            "title": f"Lead {role_cap} Architect",
            "source": "Adzuna",
            "link": linkedin_url,
            "snippet": "Join our global team to lead the development of next-gen AI applications..."
        }
    ]

# --- API ENDPOINTS ---

@app.get("/")
def home():
    return {"status": "ResumeMatch AI Brain is Active 🧠"}

@app.post("/search-jobs")
def find_jobs(role: str = Form(...), location: str = Form(""), company: str = Form("")):
    results = []
    
    # 1. Try Adzuna API (Real, Legal Data)
    if ADZUNA_APP_ID and ADZUNA_APP_KEY:
        print(f"🔎 Calling Adzuna API for: {role} in {location}")
        try:
            # Country code 'in' for India. Change to 'gb', 'us', etc. if needed.
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
                    # Adzuna results include title, description, and redirect_url
                    results.append({
                        "id": str(item.get('id')),
                        "title": item.get('title').replace("<strong>", "").replace("</strong>", ""),
                        "source": "Adzuna", 
                        "link": item.get('redirect_url'),
                        "snippet": item.get('description')[:200] + "..."
                    })
                print(f"   ✅ Found {len(results)} REAL jobs via Adzuna.")
            else:
                print(f"   ❌ Adzuna Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ API Connection Failed: {e}")

    # 2. Fallback to Demo Data if API returned nothing
    if not results:
        results = get_demo_jobs(role, location)
        
    return {"jobs": results}

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return {"filename": file_path, "message": "File uploaded"}

@app.post("/analyze-match")
async def analyze_match(filename: str = Form(...), job_title: str = Form(...), job_desc: str = Form(...)):
    if not os.path.exists(filename):
        return generate_mock_analysis()
    
    resume_text = extract_text_from_pdf(filename)
    
    if client:
        try:
            prompt = f"""
            You are an ATS Scanner. Resume: "{resume_text[:3000]}"
            Job Title: "{job_title}"
            Job Desc: "{job_desc}"
            Return JSON: match_score (0-100), missing_skills (list), improvements (list), roadmap (list).
            """
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"OpenAI Error: {e}")
            
    return generate_mock_analysis()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)