import { useState, useRef } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [filename, setFilename] = useState("");
  const [jobRole, setJobRole] = useState('');
  const [location, setLocation] = useState('');
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // AI Analysis State
  const [analysisResult, setAnalysisResult] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  
  // Ref for auto-scrolling to results
  const resultsRef = useRef(null);

  // 1. Upload Resume
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

  // 2. Search Jobs
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

  // 3. Run AI Analysis (Connected to all 4 Buttons)
  const runAnalysis = async () => {
    if (!filename) return alert("Please upload a resume first!");
    if (!selectedJob) return alert("Please select a job first!");
    
    setAnalyzing(true);
    setAnalysisResult(null); // Clear old results

    const formData = new FormData();
    formData.append('filename', filename);
    formData.append('job_title', selectedJob.title);
    formData.append('job_desc', selectedJob.snippet);

    try {
      const res = await axios.post('http://localhost:8000/analyze-match', formData);
      setAnalysisResult(res.data);
      
      // Auto-scroll to results after short delay
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
      
    } catch (err) {
      alert("Analysis failed. Check console.");
      console.error(err);
    }
    setAnalyzing(false);
  };

  return (
    <div className="app-container">
      <header>
        <h1>🔥 ResumeMatch AI</h1>
        <p className="subtitle">AI-Powered Resume Matcher & Career Architect</p>
      </header>

      {/* Top Section */}
      <div className="top-section">
        
        {/* Upload Card */}
        <div className="card">
          <h2>1. Upload Resume</h2>
          <div className="upload-zone">
            <input type="file" id="u-file" onChange={handleFileChange} accept=".pdf" style={{display:'none'}}/>
            <label htmlFor="u-file">
              <span style={{fontSize:'3rem'}}>📄</span>
              <p>{file ? <b style={{color:'green'}}>{file.name}</b> : "Click to Upload PDF"}</p>
            </label>
          </div>
        </div>

        {/* Search Card */}
        <div className="card">
          <h2>2. Find Your Target Job</h2>
          <div className="search-bar">
            <input placeholder="Job Role (e.g. Data Scientist)" value={jobRole} onChange={e=>setJobRole(e.target.value)} onKeyPress={e=>e.key==='Enter'&&searchJobs()}/>
            <input placeholder="Location" value={location} onChange={e=>setLocation(e.target.value)} onKeyPress={e=>e.key==='Enter'&&searchJobs()}/>
            <button className="primary-btn" onClick={searchJobs} disabled={loading}>
              {loading ? "..." : "Search"}
            </button>
          </div>

          <div className="job-results-container">
             {jobs.length === 0 && !loading && <p style={{textAlign:'center', color:'#999'}}>Jobs will appear here...</p>}
             {jobs.map(job => (
               <div key={job.id} className={`job-card ${selectedJob?.id === job.id ? 'selected' : ''}`} onClick={() => setSelectedJob(job)}>
                  <div className="job-info">
                    <h3>{job.title}</h3>
                    <p style={{fontSize:'0.8rem', color:'#666'}}>{job.snippet.substring(0,60)}...</p>
                  </div>
                  <span className={`badge ${job.source}`}>{job.source}</span>
               </div>
             ))}
          </div>
        </div>
      </div>

      {/* ANALYSIS SECTION */}
      {selectedJob && (
        <div className="card analysis-section">
          <h2 style={{textAlign: 'center', borderBottom: 'none'}}>
            Analyze match for: <span style={{color: '#ff4500'}}>{selectedJob.title}</span>
          </h2>
          
          {/* The 4 Buttons */}
          <div className="analysis-grid">
            <div className="analysis-option" onClick={runAnalysis}>
              <span className="icon">📊</span>
              <h3>Selection Probability</h3>
              <p style={{fontSize: '14px', color: '#666'}}>Predict hiring chance</p>
            </div>
            
            <div className="analysis-option" onClick={runAnalysis}>
              <span className="icon">🧩</span>
              <h3>Skill Gap Detection</h3>
              <p style={{fontSize: '14px', color: '#666'}}>Find missing keywords</p>
            </div>
            
            <div className="analysis-option" onClick={runAnalysis}>
              <span className="icon">📝</span>
              <h3>Resume Improver</h3>
              <p style={{fontSize: '14px', color: '#666'}}>Rewrite weak points</p>
            </div>
            
            <div className="analysis-option" onClick={runAnalysis}>
              <span className="icon">🚀</span>
              <h3>Learning Roadmap</h3>
              <p style={{fontSize: '14px', color: '#666'}}>Generate study plan</p>
            </div>
          </div>

          {/* Loading Indicator */}
          {analyzing && (
             <div style={{textAlign:'center', marginTop:'30px', fontSize:'1.2rem', color:'#ff4500', fontWeight:'bold'}}>
               ⚡ Analyzing your resume...
             </div>
          )}

          {/* RESULTS DASHBOARD */}
          {analysisResult && (
            <div className="results-container" ref={resultsRef}>
              
              {/* 1. Score */}
              <div className="result-box score-box">
                <div className="circle-chart">
                  <span>{analysisResult.match_score}%</span>
                </div>
                <h3>Match Probability</h3>
                <p>Based on keyword overlap (TF-IDF)</p>
              </div>

              {/* 2. Missing Skills */}
              <div className="result-box missing-box">
                <h3>⚠️ Missing Skills</h3>
                <ul>
                  {analysisResult.missing_skills.map((s,i) => <li key={i}>{s}</li>)}
                </ul>
              </div>

              {/* 3. Improvements */}
              <div className="result-box improve-box">
                <h3>📝 Improvement Tips</h3>
                <ul>
                  {analysisResult.improvements.map((s,i) => <li key={i}>{s}</li>)}
                </ul>
              </div>

              {/* 4. Roadmap */}
              <div className="result-box roadmap-box">
                <h3>🚀 Learning Roadmap</h3>
                <ul>
                  {analysisResult.roadmap.map((s,i) => <li key={i}>{s}</li>)}
                </ul>
              </div>

            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;