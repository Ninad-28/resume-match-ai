import { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [jobRole, setJobRole] = useState('');
  const [location, setLocation] = useState('');
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [loading, setLoading] = useState(false);

  // File Upload Handler
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  // Job Search Handler
  const searchJobs = async () => {
    if (!jobRole) return alert("Please enter a job role");
    setLoading(true);
    setSelectedJob(null); // Reset selection on new search
    
    const formData = new FormData();
    formData.append('role', jobRole);
    formData.append('location', location);
    formData.append('company', '');

    try {
      const res = await axios.post('http://localhost:8000/search-jobs', formData);
      setJobs(res.data.jobs);
    } catch (err) {
      console.error(err);
      alert("Backend connection failed. Make sure python main.py is running.");
    }
    setLoading(false);
  };

  return (
    <div className="app-container">
      <header>
        <h1>ResumeMatch AI</h1>
        <p className="subtitle">AI-Powered Resume Matcher & Career Architect</p>
      </header>

      {/* Top Section: Split into Upload and Search */}
      <div className="top-section">
        
        {/* Left Col: Upload */}
        <div className="card">
          <h2>1. Upload Resume</h2>
          <div className="upload-zone">
            <input 
              type="file" 
              id="file-upload" 
              onChange={handleFileChange} 
              accept=".pdf" 
              style={{display: 'none'}} 
            />
            <label htmlFor="file-upload" style={{cursor: 'pointer'}}>
              <span style={{fontSize: '30px'}}>📄</span>
              <p>
                {file ? <strong>{file.name}</strong> : "Click to Upload PDF Resume"}
              </p>
            </label>
          </div>
        </div>

        {/* Right Col: Job Search */}
        <div className="card">
          <h2>2. Find Your Target Job</h2>
          <div className="search-bar">
            <input 
              placeholder="Job Role (e.g. Data Scientist)" 
              value={jobRole} 
              onChange={(e) => setJobRole(e.target.value)} 
              onKeyPress={(e) => e.key === 'Enter' && searchJobs()}
            />
            <input 
              placeholder="Location (e.g. Bangalore)" 
              value={location} 
              onChange={(e) => setLocation(e.target.value)} 
              onKeyPress={(e) => e.key === 'Enter' && searchJobs()}
            />
            <button className="primary-btn" onClick={searchJobs} disabled={loading}>
              {loading ? "Searching..." : "Search"}
            </button>
          </div>

          {/* Job Results List */}
          <div className="job-results-container">
            {jobs.length === 0 && !loading && (
              <p style={{textAlign: 'center', color: '#999', marginTop: '20px'}}>
                No jobs searched yet. Try searching above!
              </p>
            )}
            
            {jobs.map((job) => (
              <div 
                key={job.id} 
                className={`job-card ${selectedJob?.id === job.id ? 'selected' : ''}`}
                onClick={() => setSelectedJob(job)}
              >
                <div className="job-info">
                  <h3>{job.title}</h3>
                  <p style={{fontSize: '13px', color: '#666', margin: '4px 0'}}>{job.snippet.substring(0, 60)}...</p>
                </div>
                <div style={{textAlign: 'right'}}>
                  <span className={`badge ${job.source}`}>{job.source}</span>
                  <br/>
                  <a 
                    href={job.link} 
                    target="_blank" 
                    rel="noreferrer" 
                    style={{fontSize: '11px', color: '#999', textDecoration: 'none', display: 'block', marginTop: '5px'}}
                    onClick={(e) => e.stopPropagation()}
                  >
                    View ↗
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Section: Analysis Dashboard */}
      {selectedJob && (
        <div className="card analysis-section">
          <h2 style={{textAlign: 'center', borderBottom: 'none'}}>
            Analyze match for: <span style={{color: '#ff4500'}}>{selectedJob.title}</span>
          </h2>
          
          <div className="analysis-grid">
            <div className="analysis-option" onClick={() => alert("Calculating Probability...")}>
              <span className="icon">📊</span>
              <h3>Selection Probability</h3>
              <p style={{fontSize: '12px', color: '#666'}}>Predict your hiring chance</p>
            </div>
            
            <div className="analysis-option" onClick={() => alert("Detecting Gaps...")}>
              <span className="icon">🧩</span>
              <h3>Skill Gap Detection</h3>
              <p style={{fontSize: '12px', color: '#666'}}>Find missing keywords</p>
            </div>
            
            <div className="analysis-option" onClick={() => alert("Suggesting Improvements...")}>
              <span className="icon">📝</span>
              <h3>Resume Improver</h3>
              <p style={{fontSize: '12px', color: '#666'}}>Rewrite weak bullet points</p>
            </div>
            
            <div className="analysis-option" onClick={() => alert("Generating Roadmap...")}>
              <span className="icon">🚀</span>
              <h3>Learning Roadmap</h3>
              <p style={{fontSize: '12px', color: '#666'}}>Personalized course plan</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;