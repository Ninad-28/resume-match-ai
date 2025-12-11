from fastapi import FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from duckduckgo_search import DDGS
import uvicorn
import json

app = FastAPI()

# 1. CORS Setup (Allows your React Frontend to talk to this Python Backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all connections (Perfect for Hackathons)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. The Search Logic
def search_jobs_on_web(role: str, location: str, company: str):
    results = []
    # Construct a smart search query to find specific links
    query = f"{role} {company} jobs in {location} site:linkedin.com/jobs OR site:naukri.com"
    print(f"🔍 Searching for: {query}")
    
    try:
        # Use DuckDuckGo to find real job postings
        with DDGS() as ddgs:
            # Get top 10 results
            search_results = list(ddgs.text(query, max_results=10))
            
            for item in search_results:
                # Detect if it's LinkedIn or Naukri based on the URL
                source = "LinkedIn" if "linkedin.com" in item['href'] else "Naukri" if "naukri.com" in item['href'] else "Other"
                
                results.append({
                    "id": item['href'],   # Use URL as a unique ID
                    "title": item['title'],
                    "source": source,
                    "link": item['href'],
                    "snippet": item['body'] # A short description of the link
                })
                
    except Exception as e:
        print(f"⚠️ Search Error: {e}")
        # If search fails, return empty list (Frontend will handle it)
        return []
        
    return results

# 3. API Endpoints

@app.get("/")
def home():
    return {"status": "ResumeMatch AI System is Online 🚀"}

@app.post("/search-jobs")
def find_jobs(
    role: str = Form(...), 
    location: str = Form(""), 
    company: str = Form("")
):
    """
    Receives Job Role, Location, and Company from Frontend.
    Returns a list of job links from LinkedIn/Naukri.
    """
    jobs = search_jobs_on_web(role, location, company)
    
    # --- DEMO FALLBACK (If no real jobs found, show these so demo doesn't fail) ---
    if not jobs:
        print("⚠️ No results found. Serving Demo Data.")
        jobs = [
            {
                "id": "demo_1",
                "title": f"Senior {role} (Demo Result)",
                "source": "LinkedIn",
                "link": "https://www.linkedin.com/jobs",
                "snippet": "We are looking for an experienced candidate..."
            },
            {
                "id": "demo_2",
                "title": f"{role} Developer (Demo Result)",
                "source": "Naukri",
                "link": "https://www.naukri.com",
                "snippet": "Urgent hiring for top MNC in Mumbai..."
            }
        ]
    # -----------------------------------------------------------------------------
    
    return {"jobs": jobs}

# 4. Resume Upload Endpoint (Placeholder for next step)
@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    return {"filename": file.filename, "message": "Resume uploaded successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)