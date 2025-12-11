import os
import json
import random
from fastapi import FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from duckduckgo_search import DDGS
from pypdf import PdfReader
import uvicorn
from openai import OpenAI

# Initialize App
app = FastAPI()

# CORS: Allow connection from your React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 1. CONFIGURATION ---
# If you have an OpenAI Key, paste it inside the quotes: "sk-..."
# If empty, the system uses "Hackathon Mode" (Mock Data).
OPENAI_API_KEY = "" 
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# --- 2. HELPER FUNCTIONS ---
def extract_text_from_pdf(file_path):
    """Reads text from the uploaded PDF file."""
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
    """Generates realistic fake data for demo purposes."""
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

# --- 3. API ENDPOINTS ---

@app.get("/")
def home():
    return {"status": "ResumeMatch AI Brain is Active 🧠"}

# JOB SEARCH ENGINE (DuckDuckGo)
# Updated Search Function in server/main.py

@app.post("/search-jobs")
def find_jobs(role: str = Form(...), location: str = Form(""), company: str = Form("")):
    results = []
    
    # 1. Search LinkedIn specific
    query_linkedin = f"{role} {company} {location} site:linkedin.com/jobs"
    print(f"🔎 Searching LinkedIn: {query_linkedin}")
    
    try:
        with DDGS() as ddgs:
            linkedin_results = list(ddgs.text(query_linkedin, max_results=5))
            for item in linkedin_results:
                results.append({
                    "id": item['href'],
                    "title": item['title'].replace(" | LinkedIn", ""), # Clean title
                    "source": "LinkedIn",
                    "link": item['href'],
                    "snippet": item['body']
                })
    except Exception as e:
        print(f"LinkedIn Search Error: {e}")

    # 2. Search Naukri specific
    query_naukri = f"{role} {company} {location} site:naukri.com"
    print(f"🔎 Searching Naukri: {query_naukri}")
    
    try:
        with DDGS() as ddgs:
            naukri_results = list(ddgs.text(query_naukri, max_results=5))
            for item in naukri_results:
                results.append({
                    "id": item['href'],
                    "title": item['title'].replace(" - Naukri.com", ""), # Clean title
                    "source": "Naukri",
                    "link": item['href'],
                    "snippet": item['body']
                })
    except Exception as e:
        print(f"Naukri Search Error: {e}")

    # 3. Fallback if both fail
    if not results:
        results = [
            {"id": "demo1", "title": f"Senior {role}", "source": "LinkedIn", "link": "https://www.linkedin.com/jobs", "snippet": "looking for experienced candidates..."},
            {"id": "demo2", "title": f"{role} Developer", "source": "Naukri", "link": "https://www.naukri.com", "snippet": "Urgent hiring in Mumbai..."}
        ]
        
    # Shuffle slightly so they are mixed (Optional)
    import random
    random.shuffle(results)
    
    return {"jobs": results}

# RESUME UPLOAD
@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    # Save file locally
    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return {"filename": file_path, "message": "File uploaded"}

# --- THE CORE AI ANALYSIS (STEP 4 LOGIC) ---
@app.post("/analyze-match")
async def analyze_match(
    filename: str = Form(...),
    job_title: str = Form(...),
    job_desc: str = Form(...)
):
    print(f"🧠 Analyzing Resume against: {job_title}")
    
    # 1. Read Resume
    if not os.path.exists(filename):
        return generate_mock_analysis() # Fallback if file missing
    
    resume_text = extract_text_from_pdf(filename)
    
    # 2. Use OpenAI (Real AI)
    if client:
        try:
            prompt = f"""
            You are an ATS Scanner. 
            Resume: "{resume_text[:3000]}"
            Job Title: "{job_title}"
            Job Desc: "{job_desc}"
            
            Return a valid JSON object with these keys:
            - match_score (integer 0-100)
            - missing_skills (list of strings)
            - improvements (list of strings, resume tips)
            - roadmap (list of strings, study plan)
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"OpenAI Error: {e}. Switching to Hackathon Mode.")
            
    # 3. Hackathon Mode (Fallback)
    # If no API key or error, return realistic mock data
    return generate_mock_analysis()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)