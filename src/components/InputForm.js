import React, { useState } from 'react';

function InputForm({ onAnalyze, isLoading, error }) {
  const [jobDescription, setJobDescription] = useState('');
  const [resumeFile, setResumeFile] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!jobDescription || !resumeFile) {
      alert('Please fill in both fields.');
      return;
    }
    onAnalyze(jobDescription, resumeFile);
  };

  return (
    <div className="input-form">
      <h2>Analyze Your Profile</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="job-description">Job Description</label>
          <textarea
            id="job-description"
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Paste the full job description here..."
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="resume-file">Upload Your Resume (.pdf, .docx)</label>
          <input
            id="resume-file"
            type="file"
            accept=".pdf,.docx"
            onChange={(e) => setResumeFile(e.target.files[0])}
            required
          />
        </div>
        <button type="submit" className="analyze-button" disabled={isLoading}>
          {isLoading ? 'Analyzing...' : 'Analyze Now'}
        </button>
        {error && <p className="error-message">{error}</p>}
      </form>
    </div>
  );
}

export default InputForm;