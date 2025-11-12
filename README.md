# 🗺️ AI Skill Mapper: Intelligent Career Pathing System

![Python](https://img.shields.io/badge/AI%20Engine-Python%203.10-blue)
![React](https://img.shields.io/badge/Frontend-React%2018-cyan)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)
![Status](https://img.shields.io/badge/Status-Active-success)

**AI Skill Mapper** is an end-to-end intelligent system designed to revolutionize how candidates approach career growth. By integrating **Natural Language Processing (NLP)** with **Machine Learning (ML)** algorithms, this application performs deep semantic analysis of resumes against job descriptions to predict success probabilities, identify critical skill gaps, and generate algorithmic learning roadmaps.

## 📜 Project Overview

In the evolving landscape of recruitment, simple keyword matching is no longer sufficient. This project implements a **Full-Stack Intelligent System** that acts as a personalized AI career coach.

Unlike traditional parsers, AI Skill Mapper utilizes a multi-stage intelligence pipeline:
1.  **NLP Foundation:** Extracts and normalizes entities from unstructured data (PDF/DOCX resumes) to understand a candidate's true profile.
2.  **Predictive ML Layer:** Applies a **Weighted Success Scoring algorithm** to evaluate candidate fit based on the semantic importance of specific technical and soft skills.
3.  **Algorithmic Pathing:** Uses topological sorting and dependency graphs to construct a logical, step-by-step learning roadmap (e.g., enforcing "Python" $\rightarrow$ "Machine Learning").
4.  **Dynamic Resource Allocation:** Interacts with the **YouTube Data API** to fetch real-time, high-relevance tutorial content for identified skill gaps.

## ✨ Key Features

* **🧠 AI-Driven Profile Analysis:** Deep extraction of skills and metadata from resumes using custom NLP pipelines (`spaCy`).
* **⚖️ Weighted ML Scoring:** A sophisticated scoring engine that assigns dynamic weights to skills based on their relevance (Technical vs. Soft), providing a precise "Fit Score" rather than a simple keyword count.
* **📉 Intelligent Gap Detection:** Automatically identifies missing critical competencies by comparing the user's normalized skill vector against the job requirements.
* **🛣️ Dependency-Aware Roadmap:** Generates a logical learning path. The system understands skill hierarchies, ensuring prerequisites are mastered before advanced topics.
* **🎥 Real-Time Content Aggregation:** A hybrid recommendation engine that fetches curated resources and live video tutorials via the **YouTube Data API v3**.
* **💻 Interactive Dashboard:** A responsive React.js interface that visualizes data analytics and learning paths in real-time.

## 💻 Tech Stack

* **AI & Backend:** Python, FastAPI, spaCy (NLP), Weighted Scoring Algorithms
* **Frontend:** React.js, CSS3, Axios
* **Data Processing:** PyMuPDF, python-docx, NumPy
* **External APIs:** Google/YouTube Data API v3

## 🚀 Setup and Installation

To run this project locally, follow these steps for both the backend and frontend.

### 1. Backend Setup (Python)

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Sreekarreddy2005/AI-Skill-Mapper.git](https://github.com/Sreekarreddy2005/AI-Skill-Mapper.git)
    cd AI-Skill-Mapper
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # Windows:
    venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install fastapi uvicorn spacy python-docx pymupdf google-api-python-client python-multipart requests
    ```

4.  **Download the NLP Model:**
    ```bash
    python -m spacy download en_core_web_sm
    ```

5.  **Configure API Key:**
    Open `intelligence/resource_finder.py` and add your **YouTube Data API Key**:
    ```python
    YOUTUBE_API_KEY = "YOUR_API_KEY_HERE"
    ```

6.  **Run the Server:**
    ```bash
    uvicorn main:app --reload
    ```
    The intelligent backend will start at `http://127.0.0.1:8000`.

### 2. Frontend Setup (React)

1.  **Navigate to the frontend directory:**
    (Open a new terminal window)
    ```bash
    cd frontend
    ```

2.  **Install Node modules:**
    ```bash
    npm install axios react react-dom react-scripts
    ```

3.  **Start the Application:**
    ```bash
    npm start
    ```
    The user interface will launch at `http://localhost:3000`.

## 🖥️ Usage Flow

1.  **Job Analysis:** Paste the full text of a Job Description (JD) into the analysis field.
2.  **Profile Ingestion:** Upload your resume in `.pdf` or `.docx` format.
3.  **AI Computation:** Click **"Analyze Now."** The system processes the text, normalizes skills, and calculates the weighted score.
4.  **Results & Action Plan:**
    * View the computed **Match Percentage**.
    * Analyze the **Skill Gap Matrix** (Matching vs. Missing).
    * Follow the **AI-Generated Roadmap**, clicking on recommended video tutorials to close your skill gaps immediately.

## 👤 Author

**Sreekar Reddy Pindi**
*NLP & Backend API Developer | AI Researcher*

## ⚠️ Disclaimer

This project is an educational tool demonstrating the application of AI and NLP in Recruitment Technology (RecTech). The predictions and scores are algorithmic estimates and should be used for guidance purposes only.
