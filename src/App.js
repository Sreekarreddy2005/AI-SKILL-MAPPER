import React, { useState } from 'react';
import axios from 'axios';
import InputForm from './components/InputForm';
import ResultsDashboard from './components/ResultsDashboard';
import './App.css';

function App() {
  // State variables to manage the application's data and flow
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // Function to handle the API call
  const handleAnalysis = async (jobDescription, resumeFile) => {
    setIsLoading(true);
    setError('');
    setAnalysisResult(null);

    const formData = new FormData();
    formData.append('job_description_text', jobDescription);
    formData.append('resume_file', resumeFile);

    try {
      // Send the data to your FastAPI backend
      const response = await axios.post('http://127.0.0.1:8000/analyze-match-with-file', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setAnalysisResult(response.data);
    } catch (err) {
      setError('An error occurred during analysis. Please try again.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  // Function to go back to the input form
  const handleReset = () => {
    setAnalysisResult(null);
    setError('');
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Skill Mapper 🗺️</h1>
        <p>Analyze job descriptions against your resume to find skill gaps and get a personalized learning plan.</p>
      </header>
      <main>
        {!analysisResult ? (
          <InputForm onAnalyze={handleAnalysis} isLoading={isLoading} error={error} />
        ) : (
          <ResultsDashboard data={analysisResult} onReset={handleReset} />
        )}
      </main>
    </div>
  );
}

export default App;