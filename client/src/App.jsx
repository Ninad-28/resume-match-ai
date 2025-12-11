import { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  // --- STATE MANAGEMENT ---
  const [file, setFile] = useState(null);
  const [filename, setFilename] = useState("");
  const [jobRole, setJobRole] = useState('');
  const [location, setLocation] = useState('');
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);

  // --- HANDLERS (Same Logic as Before) ---
  const handleFileChange = async (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    try {
      const res = await axios.post('http://localhost:8000/upload-resume', formData);
      setFilename(res.data.filename);
    } catch (err) {
      alert("Backend error: Is python running?");
    }
  };

  const searchJobs = async () => {
    if (!jobRole) return alert("Enter a job role");
    setLoading(true);
    setJobs([]);
    setSelectedJob(null);
    setAnalysisResult(null);
    
    const formData = new FormData();
    formData.append('role', jobRole);
    formData.append('location', location);
    formData.append('company', '');

    try {
      const res = await axios.post('http://localhost:8000/search-jobs', formData);
      setJobs(res.data.jobs);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const runAnalysis = async () => {
    if (!filename || !selectedJob) return alert("Upload resume & select a job!");
    setAnalyzing(true);
    const formData = new FormData();
    formData.append('filename', filename);
    formData.append('job_title', selectedJob.title);
    formData.append('job_desc', selectedJob.snippet);

    try {
      const res = await axios.post('http://localhost:8000/analyze-match', formData);
      setAnalysisResult(res.data);
    } catch (err) {
      alert("Analysis failed.");
    }
    setAnalyzing(false);
  };

  return (
    <div className="page-wrapper">
      
      {/* 1. NAVBAR */}
      <nav>
        <div className="logo">
          <span>🔥</span> IgniteRoom
        </div>
        <div className="nav-links">
          <a href="#hero">Home</a>
          <a href="#features">Features</a>
          <a href="#how-it-works">How It Works</a>
        </div>
      </nav>

      {/* 2. HERO SECTION (The Tool) */}
      <section id="hero" className="hero-section">
        <div className="hero-title">
          <h1>ResumeMatch AI</h1>
          <p>AI-Powered Resume Matcher & Career Architect</p>
        </div>

        <div className="tool-container">
          {/* Left: Upload */}
          <div className="card">
            <h3>1. Upload Resume</h3>
            <div className="upload-zone">
              <input type="file" id="u-file" onChange={handleFileChange} accept=".pdf" style={{display:'none'}}/>
              <label htmlFor="u-file">
                <span style={{fontSize:'2rem'}}>📄</span>
                <p>{file ? <b style={{color:'green'}}>{file.name}</b> : "Click to Upload PDF"}</p>
              </label>
            </div>
          </div>

          {/* Right: Search & Analyze */}
          <div className="card">
            <h3>2. Find Target Job</h3>
            <div className="search-row">
              <input placeholder="Job Role (e.g. React Dev)" value={jobRole} onChange={e=>setJobRole(e.target.value)} />
              <input placeholder="Location" value={location} onChange={e=>setLocation(e.target.value)} />
              <button className="primary-btn" onClick={searchJobs} disabled={loading}>
                {loading ? "..." : "Search"}
              </button>
            </div>

            {/* Job List */}
            <div className="job-list">
               {jobs.length === 0 && !loading && <p style={{color:'#aaa', textAlign:'center'}}>Jobs will appear here...</p>}
               {jobs.map(job => (
                 <div key={job.id} 
                      className={`job-item ${selectedJob?.id === job.id ? 'selected' : ''}`}
                      onClick={() => setSelectedJob(job)}>
                    <strong>{job.title}</strong>
                    <div style={{fontSize:'0.8rem', color:'#666'}}>{job.source}</div>
                 </div>
               ))}
            </div>

            {/* ANALYSIS BUTTON */}
            {selectedJob && (
               <div style={{marginTop: '20px', textAlign: 'center'}}>
                  <button className="primary-btn" style={{width:'100%'}} onClick={runAnalysis} disabled={analyzing}>
                    {analyzing ? "Analyzing..." : `Analyze Match for ${selectedJob.title}`}
                  </button>
               </div>
            )}
          </div>
        </div>

        {/* RESULTS POPUP (Inline for now) */}
        {analysisResult && (
          <div className="card" style={{marginTop: '30px', width: '100%', maxWidth: '1100px', background:'#fff9f5', border:'1px solid #ff4500'}}>
             <h2 style={{textAlign:'center', color:'#ff4500'}}>Match Score: {analysisResult.match_score}%</h2>
             <div style={{display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap:'20px'}}>
                <div>
                   <h4>⚠️ Missing Skills</h4>
                   <ul>{analysisResult.missing_skills.map((s,i)=><li key={i}>{s}</li>)}</ul>
                </div>
                <div>
                   <h4>📝 Improvements</h4>
                   <ul>{analysisResult.improvements.map((s,i)=><li key={i}>{s}</li>)}</ul>
                </div>
                <div>
                   <h4>🚀 Roadmap</h4>
                   <ul>{analysisResult.roadmap.map((s,i)=><li key={i}>{s}</li>)}</ul>
                </div>
             </div>
          </div>
        )}
      </section>

      {/* 3. FEATURES SECTION */}
      <section id="features" className="features-section">
        <div className="section-header">
          <h2>Everything You Need to Land Your Dream Job</h2>
          <p>Powerful features designed to help you stand out and connect with the right opportunities.</p>
        </div>
        
        <div className="features-grid">
          <div className="feature-card">
            <span className="feature-icon">🤖</span>
            <h3>AI-Powered Matching</h3>
            <p>Our advanced algorithms analyze your skills and experience to predict hiring probability.</p>
          </div>
          <div className="feature-card">
            <span className="feature-icon">🎯</span>
            <h3>Skill Gap Detection</h3>
            <p>Identify exactly which keywords and technical skills you are missing for the role.</p>
          </div>
          <div className="feature-card">
            <span className="feature-icon">📝</span>
            <h3>Resume Optimization</h3>
            <p>Get AI-generated suggestions to rewrite weak bullet points and pass ATS filters.</p>
          </div>
          <div className="feature-card">
            <span className="feature-icon">🚀</span>
            <h3>Personalized Roadmap</h3>
            <p>Receive a step-by-step learning path to bridge your skill gaps.</p>
          </div>
          <div className="feature-card">
            <span className="feature-icon">🔒</span>
            <h3>Privacy Focused</h3>
            <p>Your data is encrypted and secure. We never share your information without permission.</p>
          </div>
          <div className="feature-card">
            <span className="feature-icon">📈</span>
            <h3>Market Insights</h3>
            <p>Get real-time data on hiring trends and demand for specific roles.</p>
          </div>
        </div>
      </section>

      {/* 4. HOW IT WORKS SECTION */}
      <section id="how-it-works" className="how-it-works-section">
        <div className="section-header">
          <h2>How It Works</h2>
          <p>Four simple steps to transform your job search.</p>
        </div>

        <div className="steps-container">
          <div className="step-card">
            <div className="step-number">1</div>
            <h3>Upload Resume</h3>
            <p>Simply upload your resume in PDF format. Our system accepts all standard formats.</p>
          </div>
          <div className="step-card">
            <div className="step-number">2</div>
            <h3>Find Job</h3>
            <p>Search for your target role and select a live job posting from LinkedIn or Naukri.</p>
          </div>
          <div className="step-card">
            <div className="step-number">3</div>
            <h3>AI Analysis</h3>
            <p>Our AI compares your profile against the job description to find gaps.</p>
          </div>
          <div className="step-card">
            <div className="step-number">4</div>
            <h3>Get Hired</h3>
            <p>Follow the roadmap, improve your resume, and apply with confidence.</p>
          </div>
        </div>
      </section>

      {/* 5. FOOTER */}
      <footer>
        <div className="logo" style={{justifyContent:'center', color:'white'}}>
          <span>🔥</span> IgniteRoom
        </div>
        <p>Empowering job seekers with AI-powered resume matching.</p>
        <div className="footer-links">
          <a href="#">Privacy Policy</a>
          <a href="#">Terms of Service</a>
          <a href="#">Contact</a>
        </div>
        <p style={{marginTop:'30px', fontSize:'0.8rem', color:'#718096'}}>© 2025 IgniteRoom. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;