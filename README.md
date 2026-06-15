# 🐳 Digital recruitment platform

⚠️ **NOTE: DEMO MODE**

    transcription-fireworks uses an API, but it can also be deployed locally, folder: "stt-wispher-large-server"

    This interview is artificially shortened for quick testing of the system's functionality.
    The demo version uses a limited set of questions to demonstrate the algorithm's capabilities.

    The full interview duration and number of questions are configured in the system's code
    depending on the requirements of the specific vacancy and the seniority of the position.

    In the production version, an interview may include:
    • 15–30 technical questions
    • Adaptive difficulty based on the candidate's answers
    • Additional blocks on soft skills and cases
    • A total duration of 30–60 minutes

The project can be deployed locally using Docker.

## Project overview

**MoreTech.VTB** — an HR platform for digital recruitment. The system combines an AI-powered intelligent technical interview system, voice analysis, speech synthesis, and a convenient web interface for candidates and companies.

## Key features

### **For candidates:**

#### Profile page

    Profile management with the ability to edit user information and resume, and to track current applications


#### Job search

    Smart search with filtering and color coding of levels (Junior/Middle/Senior)

#### Company search

    A catalog of companies with detailed information and employer profiles


#### Resume check

    Resume analysis with the ability to view and edit it via AI


#### Interactive interviews

    Voice interviews with real-time speech analysis and AI feedback


#### Application tracking

    Monitoring application statuses with convenient filters and notifications

### **For HR/Companies:**

#### Candidate management

    Full candidate analysis with viewing of resume, interview results, and voice analysis


#### Interview results

    Detailed analytics with AI recommendations and per-criterion scores


#### Application management

    Changing application statuses with candidate notifications


#### Vacancy creation

    Posting vacancies and managing candidate requirements

#### HH.ru integration

    Automatic synchronization with HeadHunter:
    - Importing candidate responses
    - Synchronizing vacancies
    - Automatically creating interviews for new responses
    - Managing negotiations via the HH.ru API

#### Company analytics dashboards

    Comprehensive hiring analytics:
    - General statistics: Number of candidates, completed interviews, hired employees
    - Status distribution: Visualization of the hiring funnel (active → completed → test task → finalists → offers)
    - Score distribution: Categorization of candidates by level (excellent/good/average/weak/poor)
    - Voice characteristics analysis: Average metrics for stress resistance, communication, energy
    - Interactive charts: Detailed per-vacancy analytics with efficiency metrics
    - Report export: Downloading detailed per-vacancy reports in various formats
    - KPI metrics: Time to hire, stage-by-stage conversion, candidate quality

#### Candidate analytics dashboard

    Personal analytics for candidates:
    - Overall score: A comprehensive score based on resume and interview
    - Skill breakdown: Radial progress bars for technical and soft skills
    - Topic analysis: Charts and tables with scores across various interview topics
    - Voice analysis: Scores for stress resistance, communication, energy
    - Application statistics: Number of applications submitted, offers, rejections
    - AI recommendations: Personal tips for improving the profile


#### Company profile

    A corporate page in the style of modern HR platforms with full information about the company


## Application structure

### Interfaces for candidates

| Page                  | Path            | Description                                                                |
| --------------------------------- | ------------------- | ------------------------------------------------------------------------------- |
| **Home**          | `/`               | Main menu                                                         |
| **All vacancies** | `/vacancies-list` | Full catalog with switching to companies |
| **Profile**          | `/profile`        | Editing data and managing the resume  |
| **Interview**        | `/interview`      | Voice interviews with AI analysis                    |
| **My applications**     | `/applications`   | Status tracking with filters                           |

### Panels for HR/Companies

| Page                            | Path               | Description                                                             |
| ------------------------------------------- | ---------------------- | ---------------------------------------------------------------------------- |
| **Dashboard** | `/company-dashboard` | Statistics and quick actions                      |
| **Candidates**                | `/candidates`        | Analysis of candidates and interview results |
| **Settings**                | `/company-profile`   | Company profile in the HH.ru style                          |

---

## MongoDB database

> **Database**: `aihr_database`
> **Driver**: PyMongo
> **Total collections**: 8

## DB schema

```mermaid
erDiagram
    users ||--o{ interviews : "user_id"
    companies ||--o{ vacancies : "company_id"
    companies ||--o| company_profiles : "company_id"
    companies ||--o{ hh_responses : "our_company_id"
    vacancies ||--o{ interviews : "vacancy_id"
    vacancies ||--o{ hh_responses : "our_vacancy_id"
    interviews ||--o{ interview_answers : "interview_id"
    interviews ||--o{ status_history : "interview_id"
  
    users {
        ObjectId _id PK
        string email UK
        string password
        string name
        string surname
        string telegram_id
        string resume_path
        string role
        datetime created_at
        datetime updated_at
    }
  
    companies {
        ObjectId _id PK
        string email UK
        string password
        string company_name
        string hh_id
        string description
        string website
        string logo_url
        array industries
        object area
        string access_token
        string refresh_token
        string role
        datetime created_at
        datetime updated_at
    }
  
    company_profiles {
        ObjectId _id PK
        ObjectId company_id FK
        object basic_info
        object detailed_description
        object contact_info
        array benefits
        object social_links
        object additional_info
        datetime created_at
        datetime updated_at
    }
  
    vacancies {
        ObjectId _id PK
        ObjectId company_id FK
        string hh_id
        string title
        string grade
        int min_experience
        int max_experience
        array required_skills
        array optional_skills
        string description
        string work_field
        string work_address
        object salary
        object area
        array questions
        datetime created_at
        datetime updated_at
    }
  
    interviews {
        ObjectId _id PK
        ObjectId user_id FK
        ObjectId vacancy_id FK
        string status
        int resume_score
        object resume_analysis
        object interview_analysis
        string recommendation
        string rejection_reason
        datetime created_at
        datetime updated_at
    }
  
    interview_answers {
        ObjectId _id PK
        ObjectId interview_id FK
        string mlinterview_id
        string question
        string answer_text
        string status
        object report
        string recommendation
        object voice_analysis
        int optimal_time
        string video_id
        datetime created_at
    }
  
    status_history {
        ObjectId _id PK
        ObjectId interview_id FK
        ObjectId user_id FK
        ObjectId vacancy_id FK
        string status
        datetime created_at
    }

    hh_responses {
        ObjectId _id PK
        string hh_negotiation_id
        string hh_resume_id
        string hh_vacancy_id
        ObjectId our_company_id FK
        ObjectId our_vacancy_id FK
        string vacancy_name
        object negotiation_state
        object resume_data
        object negotiation_data
        datetime created_at
        datetime updated_at
        datetime imported_at
    }
```

## AI-HR Service (Port 8002)

### Key features

- **Adaptive interviewing** — the system adapts to the candidate's answers
- **Detailed scoring** — a 6-criteria scoring system with weighting coefficients
- **Smart control** — automatic decisions about continuing/skipping topics
- **Detailed reports** — structured reports with hiring recommendations
- **REST API** — full integration with external HR systems
- **Job Matching** — assessing how well a resume matches the vacancy requirements
- **Voice analysis** — a WebSocket service for analyzing speech and soft skills
- **Reliability** — error handling and fallback mechanisms

## System architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[Web Interface]
        B[Mobile App]
        C[HR Systems]
    end
  
    subgraph "API Layer"
        D[FastAPI Server]
        E[Authentication]
        F[Rate Limiting]
    end
  
    subgraph "Core System"
        G[Interview System]
        H[Job Matching]
        I[RAG System]
        V[Voice Analysis]
    end
  
    subgraph "AI Agents"
        J[Planner Agent]
        K[Question Selector]
        L[Conversation Manager]
        M[Answer Evaluator]
        N[Adaptive Controller]
        O[Report Generator]
    end
  
    subgraph "Data Layer"
        P[ChromaDB]
        Q[Knowledge Base]
        R[Interview History]
    end
  
    subgraph "External Services"
        S[OpenRouter API]
        T[HuggingFace Models]
        U[Whisper API]
    end
  
    A --> D
    B --> D
    C --> D
    D --> G
    D --> H
    G --> J
    G --> K
    G --> L
    G --> M
    G --> N
    G --> O
    I --> P
    I --> Q
    G --> S
    I --> T
    V --> U
```

## Detailed guide

### Main components

#### 1. **Agent-based interview system** (`ml_system/interview_system.py`)

The central component that manages the entire interview process:

- **6 specialized agents** for different tasks
- **Adaptive control** based on the candidate's answers
- **Strict limits** to prevent looping
- **Detailed analytics** with data aggregation

#### 2. **RAG system** (`ml_system/retrieva.py`)

A system for searching and retrieving relevant questions:

- **ChromaDB** for vector search
- **HuggingFace Embeddings** for semantic understanding
- **Knowledge base** with 99+ structured questions
- **Variety** by topic and question format (not tied to levels)

#### 3. **Job Matching** (`ml_system/job_matching.py`)

Assessing how well a resume matches the vacancy requirements:

- **Flexible weighting system** for different criteria
- **Automatic extraction** of data from the resume
- **Penalties** for lack/excess of experience
- **Detailed breakdown** by criteria

#### 4. **REST API** (`api.py`)

A full-featured API for integration:

- **FastAPI** with automatic documentation
- **Pydantic** for data validation
- **Asynchronous** request processing
- **Error handling** and fallback mechanisms

#### 5. **Voice analysis (WebSocket)** (`ml_system/voice_analyser.py`)

An innovative real-time speech analysis system:

- **WebSocket endpoint** `/ws/voice` for streaming audio processing
- **Whisper transcription** — accurate speech recognition in Russian
- **Acoustic analysis** — feature extraction using librosa
- **Soft-skill detection** — automatic detection of communication skills
- **Real-time processing** — analysis of audio chunks in real time

### System configuration

#### Interview limits

Limits are set by the `InterviewSystem` constructor parameters and the controller logic:

- `max_total_questions` — the overall question limit (default ~7–30 depending on the configuration)
- `max_questions_per_topic` — the question limit per topic
- The controller limits the number of follow-up questions and hints (see the `AdaptiveInterviewControllerAgent` class)

#### Scoring criteria

The model returns strict JSON with keys (0..10), after which a weighted final score is computed:

```json
{
  "technical_accuracy": 0,
  "depth_of_knowledge": 0,
  "practical_experience": 0,
  "communication_clarity": 0,
  "problem_solving_approach": 0,
  "examples_and_use_cases": 0,
  "inconsistencies": ["…"],
  "red_flags": ["…"],
  "strengths": ["…"],
  "weaknesses": ["…"],
  "follow_up_suggestions": ["…"]
}
```

By default, the weighting coefficients inside the system are distributed between technical and communication aspects (see the `_answer_evaluator` implementation).

#### Decision thresholds

By default, the final recommendation is formed in the reports based on the average score and the identified risks. There is no hard binding to the candidate's level.

## API documentation

### Endpoints

#### 1. Creating an interview

```http
POST /interviews
Content-Type: application/json

{
  "resume": "Experience with Python/ML, projects on classification and regression...",
  "job_description": "Python skills required, ML libraries, working with data"
}
```

**Response:**

```json
{
  "interview_id": "b77aac53-b263-4f0c-9f27-6aa4aa2cd30e",
  "status": "waiting_for_answer",
  "current_question": "Describe the most significant project from your resume: the goal, your contribution, the result.",
  "question_source": "RAG/Fallback",
  "current_topic": "Resume Discussion",
  "progress": {
    "questions_asked": 0,
    "total_topics": 8,
    "current_topic": "Resume Discussion"
  }
}
```

#### 2. Submitting an answer

```http
POST /interviews/{interview_id}/answer
Content-Type: application/json

{
  "interview_id": "b77aac53-b263-4f0c-9f27-6aa4aa2cd30e",
  "answer": "I worked on a review classification project; we deployed a pipeline, AUC=0.89"
}
```

#### 3. Getting the status

```http
GET /interviews/{interview_id}/status
```

#### 4. Resume scoring

```http
POST /resume-match
Content-Type: application/json

{
  "resume": "Python developer with ML experience...",
  "required_skills": ["Python", "scikit-learn", "pandas"],
  "optional_skills": ["tensorflow", "SQL", "Docker"],
  "min_experience": 2.0,
  "max_experience": 5.0,
  "education_required": "higher education"
}
```

#### 5. Voice analysis (WebSocket)

```javascript
// Connecting to the WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/voice');

// Sending an audio chunk
ws.send(JSON.stringify({
  "audio_chunk": "base64_encoded_audio_data",
  "chunk_id": 1,
  "is_final": false
}));

// Receiving the result
ws.onmessage = function(event) {
  const result = JSON.parse(event.data);
  console.log('Transcript:', result.transcript);
  console.log('Soft-skills:', result.soft_skills_tags);
};
```

### Automatic documentation

After the server starts, interactive documentation is available:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Usage examples

### Example 1: Basic interview

```python
from ml_system.interview_system import InterviewSystem

# Initialization
system = InterviewSystem(api_key="your_api_key")
system.load_knowledge("data/ml_interview_bank_ru.json")

# Running the interview
resume = """
Experienced Python developer with 3 years of experience in machine learning.
Worked with the scikit-learn, pandas, numpy, tensorflow libraries.
Has experience building ML models for classification and regression.
"""

job_description = """
Looking for a Middle ML developer to work on NLP and Computer Vision projects.
Requirements: Python, ML libraries, experience with data, knowledge of SQL.
"""

final_state = system.run_interview(resume, job_description)
report = system.get_report(final_state)
print(report)
```

### Example 2: Using the API

```python
import requests

# Creating an interview
response = requests.post("http://localhost:8000/interviews", json={
    "resume": "ML experience, Python, pandas, sklearn",
    "job_description": "Projects with NLP/CV, data processing, SQL"
})

interview_data = response.json()
interview_id = interview_data["interview_id"]

# Submitting answers
while interview_data["status"] != "completed":
    answer = input(f"Question: {interview_data['current_question']}\nYour answer: ")
  
    response = requests.post(
        f"http://localhost:8000/interviews/{interview_id}/answer",
        json={"interview_id": interview_id, "answer": answer}
    )
  
    interview_data = response.json()

print(f"Report: {interview_data['report']}")
```

### Example 3: Job Matching

```python
from ml_system.job_matching import FlexibleResumeMatcher

# Creating the matcher
matcher = FlexibleResumeMatcher(
    required_skills=["Python", "scikit-learn", "pandas"],
    optional_skills=["tensorflow", "SQL", "Docker"],
    min_experience=2.0,
    max_experience=5.0,
    education_required="higher education"
)

# Scoring the resume
result = matcher.evaluate(resume_text)
print(f"Match: {result['total_score_percent']}%")
print(f"Details: {result['details']}")
```

## Monitoring and debugging

### Logging

The system keeps detailed logs of all operations:

```python
# Enabling detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Logs are saved in the logs/ folder
# Format: interview_api_YYYYMMDD.log
```

### Real-time metrics

```python
# Counters are displayed in the console
📊 Questions asked: 3/30
📊 Current topic: 0/8
🔍 Follow-up questions: 1/3
💡 Hints given: 0/2
```

### Agent debugging

```python
# Enabling debug mode
system = InterviewSystem(api_key="your_key", debug=True)

# Detailed information about the agents' decisions
--- Agent: Adaptive interview controller ---
📊 Latest scores: [75, 82, 68]
📉 Poor in a row: 0, Good in a row: 2, Average in a row: 1
🎯 Decision: increase_difficulty
```

## Development and extension

### Adding new agents

```python
class CustomAgent:
    def __init__(self, llm):
        self.llm = llm
  
    def execute(self, state: Dict) -> Dict:
        # Agent logic
        return {"custom_field": "value"}

# Integration into the system
system.add_agent("custom", CustomAgent(llm))
```

### Extending the knowledge base

```python
# Adding new questions
new_questions = [
    {
        "section": "New Technology",
        "question": "What is the new technology?",
        "grade": "Middle",
        "answers": {
            "expected_answer": "The main answer",
            "junior_level": "What to expect from a junior",
            "middle_level": "What to expect from a middle",
            "senior_level": "What to expect from a senior"
        }
    }
]

system.knowledge_system.add_knowledge_to_rag(new_questions)
```

### Customizing the scoring criteria

```python
# Changing the scoring weights
CUSTOM_WEIGHTS = {
    "technical_accuracy": 0.60,      # Increase importance
    "depth_understanding": 0.25,     # Increase importance
    "practical_experience": 0.10,    # Decrease importance
    "communication": 0.05            # Decrease importance
}

system.set_evaluation_weights(CUSTOM_WEIGHTS)
```

## Performance and scaling

### Recommended specifications

- **CPU:** 4+ cores
- **RAM:** 8+ GB
- **Storage:** 10+ GB of free space
- **Network:** A stable internet connection

### Performance optimization

```python
# Configuration for high loads
system = InterviewSystem(
    api_key="your_key",
    max_concurrent_interviews=10,
    cache_embeddings=True,
    batch_size=32
)
```

### Resource monitoring

```python
# Tracking resource usage
import psutil

def monitor_resources():
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory().percent
  
    if cpu_percent > 80:
        print("⚠️ High CPU load")
    if memory_percent > 80:
        print("⚠️ High memory consumption")
```

## Security

### Protecting API keys

```python
# Using environment variables
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

# Key validation
if not api_key or "your" in api_key.lower():
    raise ValueError("Invalid API key")
```

### Access restriction

```python
# CORS configuration
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### Data validation

```python
# Strict validation of input data
from pydantic import BaseModel, validator

class InterviewRequest(BaseModel):
    resume: str
    job_description: str
  
    @validator('resume')
    def validate_resume(cls, v):
        if len(v) < 50:
            raise ValueError('Resume is too short')
        return v
```

### Test examples

```python
# tests/test_interview_system.py
import pytest
from ml_system.interview_system import InterviewSystem

def test_interview_creation():
    system = InterviewSystem("test_key")
    assert system is not None

def test_evaluation_weights():
    system = InterviewSystem("test_key")
    weights = system.get_evaluation_weights()
    assert sum(weights.values()) == 1.0

@pytest.mark.asyncio
async def test_api_endpoints():
    # Testing the API endpoints
    pass
```

## Agents

## Agent system architecture

```mermaid
flowchart TD
    Start([Interview start]) --> Planner[📋 Planner<br/>Interview planner]
  
    Planner --> |Creates a plan from resume/JD| Selector[🎯 Question Selector<br/>Question selector]
  
    Selector --> |Selects a question by topic| ConvManager[💬 Conversation Manager<br/>Dialogue manager]
  
    ConvManager --> |Shows the question,<br/>gets the answer| Evaluator[📊 Answer Evaluator<br/>Answer evaluator]
  
    Evaluator --> |Evaluates via LLM| Controller[🧠 Adaptive Controller<br/>Adaptive controller]
  
    Controller --> Router{🔀 Router<br/>Decision router}
  
    Router --> |Continue with<br/>Generated Question| ConvManager
    Router --> |Skip Topic /<br/>Continue Standard| Selector
    Router --> |Finish Interview /<br/>Max Questions| Reporter[📄 Report Generator<br/>Report generator]
  
    Selector --> |All Topics<br/>Finished| Reporter
  
    Reporter --> End([Final report<br/>and recommendation])
  
    style Start fill:#2E4053,color:white
    style End fill:#1A535C,color:white
    style Planner fill:#E27D60,color:white
    style Selector fill:#85CDCA,color:black
    style ConvManager fill:#41B3A3,color:white
    style Evaluator fill:#E8A87C,color:black
    style Controller fill:#C38D9E,color:white
    style Router fill:#659DBD,color:white
    style Reporter fill:#379683,color:white
```

## State class

```python
classDiagram
    class InterviewState {
        +resume: str
        +job_description: str
        +role: str
        +interview_plan: Dict
        +current_topic: str
        +current_question: Dict
        +last_candidate_answer: str
        +messages: List
        +answer_evaluations: List[Dict]
        +questions_asked_count: int
        +questions_in_current_topic: int
        +deepening_questions_count: int
        +hints_given_count: int
        +current_topic_index: int
        +asked_question_ids: Set[str]
        +final_recommendation: str
        +report: str
        +generated_question: Dict
        +controller_decision: str
        +completed_topics: Set[str]
        +skip_topic: bool
        +question_type: str
        +last_question_type: str
    }
```

## System agents

The system is built as an **intelligent interviewer robot** consisting of **6 specialized agents**, each of which performs a specific role in the interview process:

### 1. **Interview planner** — "The Strategist"

**Class:** `InterviewPlannerAgent`
**Function:** Analyzes the resume and the job description, and creates a personalized interview plan

**Capabilities:**

- **Smart analysis** of the resume and the vacancy requirements
- **Plan generation** in strict JSON format (no markdown)
- **Adaptive limits:** up to 6 questions per topic, up to 30 questions total
- **Starting topic:** always "Resume Discussion" to discuss experience
- **Result:** a structured plan of 8 topic blocks

### 2. **Question selector** — "The Knowledge Curator"

**Class:** `QuestionSelectorAgent`
**Function:** Intelligent search and selection of relevant questions from the knowledge base

**Capabilities:**

- **Semantic search** via ChromaDB and HuggingFace embeddings
- **Knowledge base** with 99+ structured questions
- **Contextual relevance** not tied to the candidate's level
- **Deduplication** — tracking questions already asked
- **Fallback mechanism** for generating questions when none are in the base

### 3. **Dialogue manager** — "The Conversation Moderator"

**Class:** `ConversationManagerAgent`
**Function:** Manages the flow of dialogue and interaction with the candidate

**Capabilities:**

- **Phrasing questions** in a natural style
- **Generating follow-up questions** based on context
- **Creating hints** when the candidate struggles
- **Separate counting** of main and auxiliary questions
- **Maintaining a history** of the dialogue while preserving context

### 4. **Answer evaluator** — "The Expert Analyst"

**Class:** `AnswerEvaluatorAgent`
**Function:** Multi-criteria evaluation of the quality of the candidate's answers

**Scoring criteria (0–10 points):**

- **technical_accuracy** — the technical accuracy of the answer
- **depth_of_knowledge** — the depth of understanding of the topic
- **practical_experience** — practical experience
- **communication_clarity** — clarity of expression
- **problem_solving_approach** — the approach to solving problems
- **examples_and_use_cases** — examples and use cases

**Additional analysis:**

- Identifying inconsistencies and red flags
- Determining strengths and weaknesses
- Recommendations for further questions

### 5. **Adaptive controller** — "The Tactical Coordinator"

**Class:** `AdaptiveInterviewControllerAgent`
**Function:** Making decisions about the direction of the interview based on the analysis of answers

**Adaptation strategies:**

- **Deepening the topic** for good answers (generating more difficult questions)
- **Maintaining the level** for average answers
- **Simplifying/hints** for weak answers
- **Switching topics** when limits are reached or performance is low

**Limit control:**

- A maximum of 2 follow-up questions in a row
- A maximum of 1 hint in a row
- Tracking 3+ poor/good answers in a row
- Automatic switching between topics

### 6. **Report generator** — "The Final Analyst"

**Class:** `ReportGeneratorAgent`
**Function:** Creating a comprehensive report on the interview results

**Report components:**

- **Aggregated scores** across all criteria
- **Analysis of the candidate's strengths**
- **Identified weaknesses** and areas for development
- **Red flags** and inconsistencies in the answers
- **Final recommendation:** HIRE/MAYBE/REJECT
- **Justification of the decision** with concrete examples
- **Recommendations** for the HR team

## Decision-making diagram

```mermaid
flowchart TD
    Start([🧠 Adaptive controller<br/>State analysis]) --> CheckLimits{🔍 Limit check}
    
    CheckLimits --> |Topic question limit<br/>reached| SkipTopic[🚀 Skip the topic<br/>Skip Topic]
    CheckLimits --> |Follow-up limit >= max<br/>Reset the counter| SameLevel[📊 Same-level question<br/>Same Level Question]
    CheckLimits --> |Hint limit >= max<br/>Reset the counter| SameLevel
    CheckLimits --> |Limits are fine| CheckUnknown{❓ "I don't know" answer?}
    
    CheckUnknown --> |LLM detected<br/>uncertainty/lack of knowledge| CheckHintLimit{💡 Hints < max?}
    CheckUnknown --> |Substantive answer| CheckFlags{🚩 Inconsistencies or<br/>red flags?}
    
    CheckHintLimit --> |A hint can be given| ProvideHint[💡 Provide a hint<br/>Provide Hint]
    CheckHintLimit --> |Hint limit exhausted| SameLevel
    
    CheckFlags --> |Problems detected| DeepenTopic[🔬 Deepen the topic<br/>Deepen Topic]
    CheckFlags --> |No problems| CheckStreaks{📊 Answer streak analysis}
    
    CheckStreaks --> |Poor answers >= max_poor| SkipTopic
    CheckStreaks --> |Good answers >= max_good| SkipTopic
    CheckStreaks --> |Average answers >= max_medium| SkipTopic
    CheckStreaks --> |Streaks are fine| CheckLastScore{📈 Last score}
    
    CheckLastScore --> |Score >= 70%<br/>Excellent result| DeepenTopic
    CheckLastScore --> |Score 40-69%<br/>Average result| SameLevel
    CheckLastScore --> |Score < 40%<br/>Weak result| ProvideHint
    
    %% Styles for better readability
    classDef startStyle fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#000
    classDef decisionStyle fill:#fff8e1,stroke:#f57c00,stroke-width:2px,color:#000
    classDef skipStyle fill:#ffebee,stroke:#d32f2f,stroke-width:2px,color:#000
    classDef continueStyle fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#000
    classDef hintStyle fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000
    classDef deepenStyle fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    
    class Start startStyle
    class CheckLimits,CheckUnknown,CheckHintLimit,CheckFlags,CheckStreaks,CheckLastScore decisionStyle
    class SkipTopic skipStyle
    class SameLevel continueStyle
    class ProvideHint hintStyle
    class DeepenTopic deepenStyle
```

## Backend (Flask) — Launch guide and API

This service is a Flask REST API for the recruitment and interviewing platform. It works with MongoDB, integrates with the AI service for resume and interview scoring, supports uploading resumes to Yandex Object Storage, and CORS for the frontend.

### Technologies

- **Flask 3** (+ CORS)
- **MongoDB** (pymongo)
- **JWT** (PyJWT)
- **bcrypt** (password hashing)
- **Yandex Object Storage** (boto3) — optional

### Project structure (backend)

- `run.py` — entry point
- `config.py` — configuration
- `app/__init__.py` — the application factory and blueprint registration
- `app/auth` — authentication and registration
- `app/users` — user profile and resume
- `app/companies` — company profile and avatar
- `app/vacancies` — vacancy CRUD and questions
- `app/interviews` — resume checks, interviews, answers, statuses
- `app/core` — DB, decorators (`token_required`, `roles_required`), utilities
- `app/services` — working with S3, AI-HR

### Environment variables (.env)

- `MONGO_URI` — the MongoDB connection string (required)
- `SECRET_KEY` — the key for signing JWTs (required)
- `AI_HR_SERVICE_URL` — the AI service URL (default `http://127.0.0.1:8002`, in docker-compose — `http://ai-hr:8002`)
- `YC_STORAGE_BUCKET` — the bucket name in Yandex Object Storage (if used)
- `OPENROUTER_API_KEY` — the AI key (used in the ai-hr service)

Example `.env` (in the repository root):

```
MONGO_URI=mongodb://user:pass@host:27017/dbname
SECRET_KEY=change-me
AI_HR_SERVICE_URL=http://ai-hr:8002
YC_STORAGE_BUCKET=my-bucket
```

### Installation and local launch

Requires Python 3.11+ and a running MongoDB.

1) Install the dependencies (you can use the Dockerfile, but it's simpler locally):

```
pip install Flask==3.0.3 flask-cors==4.0.1 pymongo==4.10.1 python-dotenv==1.0.1 requests==2.32.3 boto3==1.35.71 PyPDF2==3.0.1 python-docx==1.1.2 bcrypt==4.2.0 PyJWT==2.9.0
```

2) Create a `.env` in the root (see above).
3) Start the backend:

```
cd backend
python run.py
```

The service will come up on `http://127.0.0.1:5000`.

### Launching via Docker (recommended, together with the frontend and services)

The project root contains a `docker-compose.yml` that brings up the frontend, backend, ai-hr, transcription, and tts.

1) Create a `.env` in the root (see above)
2) Run:

```
docker compose up -d --build
```

The backend will be available at `http://localhost:5000`.

### Authentication

- Login issues a JWT: `POST /login` (email, password)
- The token is passed in the `Authorization: Bearer <token>` header
- Resources may have role restrictions: `user` or `company`

### Resume storage

- By default, files may be saved locally in `uploads/resumes`
- If `YC_STORAGE_BUCKET` and correct environment keys are present, Yandex Object Storage is used

### Detailed API description

#### AUTHORIZATION (`app/auth/routes.py`)

**POST /login** — Login for a user or a company

```json
// Request
{
  "email": "user@example.com",
  "password": "password123"
}

// Response (200)
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "role": "user" // or "company"
}

// Errors: 400 (incomplete data), 401 (invalid data)
```

**POST /register** — User registration with a resume

```javascript
// Request (multipart/form-data)
const formData = new FormData();
formData.append('email', 'user@example.com');
formData.append('password', 'password123');
formData.append('name', 'Ivan');
formData.append('surname', 'Ivanov');
formData.append('telegram_id', '@ivanov');
formData.append('resume', file); // PDF/DOC/DOCX

// Response (201)
{
  "message": "User registered successfully"
}

// Errors: 400 (missing file/invalid type), 409 (email already exists)
```

**POST /register/company** — Company registration

```json
// Request
{
  "company_name": "Roga i Kopyta LLC",
  "inn": "1234567890",
  "ogrn": "1234567890123",
  "legal_address": "Moscow, Primernaya St., 1",
  "email": "hr@company.com",
  "password": "password123"
}

// Response (201)
{
  "message": "Company registered successfully"
}

// Errors: 400 (incomplete data), 409 (company already exists)
```

#### USERS (`app/users/routes.py`)

**GET /profile** — Get the current user's profile

```json
// Response (200)
{
  "email": "user@example.com",
  "telegram_id": "@ivanov",
  "name": "Ivan",
  "surname": "Ivanov",
  "role": "user",
  "resume_path": "https://storage.yandexcloud.net/bucket/resumes/user_resume.pdf"
}

// Errors: 404 (user not found)
```

**PUT /user/updateprofile** — Update the user's profile

```json
// Request
{
  "name": "Ivan",
  "surname": "Petrov",
  "telegram_id": "@petrov"
}

// Response (200)
{
  "message": "Profile updated successfully"
}

// Errors: 400 (no data), 404 (user not found)
```

**GET /download-resume** — Download the current user's resume

```javascript
// Response: a file with headers
Content-Type: application/pdf
Content-Disposition: attachment; filename="resume.pdf"
Content-Length: 12345

// Errors: 404 (resume not found), 500 (S3 error)
```

**POST /update-resume** — Replace the user's resume

```javascript
// Request (multipart/form-data)
const formData = new FormData();
formData.append('resume', newFile); // PDF/DOC/DOCX

// Response (200)
{
  "message": "Resume updated successfully",
  "resume_path": "https://storage.yandexcloud.net/bucket/resumes/new_resume.pdf"
}

// Errors: 400 (no file/invalid type), 404 (user not found)
```

**GET /download-candidate-resume?user_id=...** — Download a candidate's resume (companies only)

```javascript
// Response: a file with headers (similar to /download-resume)
// Errors: 400 (no user_id), 404 (candidate/resume not found)
```

**GET /user-interviews** — A list of the user's interviews

```json
// Response (200)
{
  "interviews": [
    {
      "_id": "64f1a2b3c4d5e6f7a8b9c0d1",
      "user_id": "64f1a2b3c4d5e6f7a8b9c0d2",
      "vacancy_id": "64f1a2b3c4d5e6f7a8b9c0d3",
      "status": "active",
      "resume_score": 85,
      "created_at": "2023-09-01T10:00:00Z"
    }
  ]
}
```

**GET /user-interviews-status-changes** — History of status changes

```json
// Response (200)
{
  "status_changes": [
    {
      "_id": "64f1a2b3c4d5e6f7a8b9c0d4",
      "interview_id": "64f1a2b3c4d5e6f7a8b9c0d1",
      "user_id": "64f1a2b3c4d5e6f7a8b9c0d2",
      "vacancy_id": "64f1a2b3c4d5e6f7a8b9c0d3",
      "company_id": "64f1a2b3c4d5e6f7a8b9c0d5",
      "status": "completed",
      "updated_at": "2023-09-01T15:00:00Z"
    }
  ]
}
```

#### COMPANIES (`app/companies/routes.py`)

**GET /company** — Company data (companies only)

```json
// Response (200)
{
  "email": "hr@company.com",
  "inn": "1234567890",
  "ogrn": "1234567890123",
  "company_name": "Roga i Kopyta LLC",
  "legal_address": "Moscow, Primernaya St., 1",
  "role": "company"
}

// Errors: 404 (company not found)
```

**POST /company/avatar** — Uploading a company avatar

```javascript
// Request (multipart/form-data)
const formData = new FormData();
formData.append('avatar', imageFile); // JPG/PNG

// Response (200)
{
  "message": "Avatar saved successfully",
  "avatar_url": "/company_avatars/roga_i_kopyta.jpg"
}

// Errors: 400 (no file), 404 (company not found)
```

**GET /companies?page=1&per_page=10** — A list of companies

```json
// Response (200)
{
  "total": 25,
  "page": 1,
  "per_page": 10,
  "total_pages": 3,
  "companies": [
    {
      "_id": "64f1a2b3c4d5e6f7a8b9c0d5",
      "company_name": "Roga i Kopyta LLC",
      "inn": "1234567890",
      "ogrn": "1234567890123",
      "legal_address": "Moscow, Primernaya St., 1",
      "email": "hr@company.com",
      "role": "company"
    }
  ]
}

// Errors: 400 (invalid pagination parameters)
```

**PUT /company/updateprofile** — Updating the company profile

```json
// Request
{
  "company_name": "New Name LLC",
  "inn": "0987654321",
  "ogrn": "3210987654321",
  "legal_address": "St. Petersburg, Novaya St., 2"
}

// Response (200)
{
  "message": "Company profile updated successfully"
}

// Errors: 400 (no data), 404 (company not found)
```

#### VACANCIES (`app/vacancies/routes.py`)

**POST /vacancies/create** — Create a vacancy (companies only)

```json
// Request
{
  "title": "Python Developer",
  "grade": "Middle",
  "required_skills": ["Python", "Django", "PostgreSQL"],
  "min_experience": 2,
  "max_experience": 5,
  "work_field": "Backend Development",
  "work_address": "Moscow, Rabochaya St., 1",
  "optional_skills": ["Redis", "Docker"],
  "description": "Developing web applications in Python",
  "questions": [
    "Tell us about your experience with Django",
    "How do you test your code?"
  ]
}

// Response (201)
{
  "message": "Vacancy created successfully",
  "vacancy_id": "64f1a2b3c4d5e6f7a8b9c0d6"
}

// Errors: 400 (incomplete data), 500 (save error)
```

**GET /vacancies?page=1&per_page=10&company_id=...** — A list of vacancies

```json
// Response (200)
{
  "total": 15,
  "page": 1,
  "per_page": 10,
  "total_pages": 2,
  "vacancies": [
    {
      "_id": "64f1a2b3c4d5e6f7a8b9c0d6",
      "company_id": "64f1a2b3c4d5e6f7a8b9c0d5",
      "title": "Python Developer",
      "grade": "Middle",
      "required_skills": ["Python", "Django"],
      "min_experience": 2,
      "max_experience": 5,
      "work_field": "Backend Development",
      "work_address": "Moscow",
      "optional_skills": ["Redis"],
      "description": "Developing web applications",
      "questions": ["Tell us about Django"],
      "created_at": "2023-09-01T10:00:00Z"
    }
  ]
}

// Errors: 400 (invalid parameters)
```

**POST /vacancies/{vacancy_id}/questions** — Set questions for a vacancy (owner)

```json
// Request
{
  "questions": [
    "Tell us about your experience with Python",
    "How do you approach code testing?",
    "Describe a difficult problem you solved"
  ]
}

// Response (200)
{
  "message": "Vacancy questions updated successfully"
}

// Errors: 400 (invalid format), 403 (no permission), 404 (vacancy not found)
```

**GET /vacancies/{vacancy_id}/questions** — Get a vacancy's questions

```json
// Response (200)
{
  "vacancy_id": "64f1a2b3c4d5e6f7a8b9c0d6",
  "title": "Python Developer",
  "questions": [
    "Tell us about your experience with Python",
    "How do you approach code testing?"
  ]
}

// Errors: 400 (invalid ID), 404 (vacancy not found)
```

**PUT /vacancies/{vacancy_id}** — Update a vacancy (owner)

```json
// Request
{
  "title": "Senior Python Developer",
  "grade": "Senior",
  "required_skills": ["Python", "Django", "FastAPI"],
  "min_experience": 5,
  "max_experience": 8,
  "description": "Developing high-load systems"
}

// Response (200)
{
  "message": "Vacancy updated successfully"
}

// Errors: 400 (no data), 403 (no permission), 404 (vacancy not found)
```

**DELETE /vacancies/{vacancy_id}** — Delete a vacancy (owner)

```json
// Response (200)
{
  "message": "Vacancy deleted successfully"
}

// Errors: 403 (no permission), 404 (vacancy not found), 500 (delete error)
```

**GET /vacancies/{vacancy_id}/candidates** — Candidates for a vacancy (owner)

```json
// Response (200)
{
  "total": 5,
  "page": 1,
  "per_page": 20,
  "total_pages": 1,
  "vacancy_title": "Python Developer",
  "candidates": [
    {
      "_id": "64f1a2b3c4d5e6f7a8b9c0d7",
      "user_id": "64f1a2b3c4d5e6f7a8b9c0d2",
      "vacancy_id": "64f1a2b3c4d5e6f7a8b9c0d6",
      "status": "completed",
      "resume_score": 85,
      "interview_analysis": "The candidate demonstrated good knowledge of Python...",
      "recommendation": "Recommended for hire",
      "created_at": "2023-09-01T10:00:00Z",
      "user_name": "Ivan Ivanov",
      "user_email": "ivan@example.com"
    }
  ]
}

// Errors: 400 (invalid parameters), 403 (no permission), 404 (vacancy not found)
```

#### INTERVIEWS (`app/interviews/routes.py`)

**POST /check-resume** — Check how well a resume matches a vacancy (users only)

```json
// Request
{
  "vacancy_id": "64f1a2b3c4d5e6f7a8b9c0d6"
}

// Response (200)
{
  "success": true,
  "resume_score": 85,
  "can_proceed": true,
  "message": "Resume check completed successfully",
  "interview_id": "64f1a2b3c4d5e6f7a8b9c0d7"
}

// On a low score (< 20):
{
  "success": true,
  "resume_score": 15,
  "can_proceed": false,
  "message": "Unfortunately, your resume does not meet the requirements of this vacancy"
}

// Errors: 400 (no vacancy_id/resume), 404 (vacancy/user not found)
```

**POST /convert-resume** — Check whether the interview is ready (users only)

```json
// Request
{
  "vacancy_id": "64f1a2b3c4d5e6f7a8b9c0d6"
}

// Response (200)
{
  "interview_id": "64f1a2b3c4d5e6f7a8b9c0d7",
  "message": "The interview is ready to start"
}

// Errors: 400 (resume not checked), 403 (resume rejected), 404 (not found)
```

**POST /interviews/answer** — Submit an answer in an interview (users only)

```json
// First request (interview start)
{
  "interview_id": "64f1a2b3c4d5e6f7a8b9c0d7",
  "mlinterview_id": "",
  "answer_text": ""
}

// Response (201)
{
  "interview_id": "64f1a2b3c4d5e6f7a8b9c0d7",
  "mlinterview_id": "ai_interview_123",
  "question": "Tell us about yourself and your work experience",
  "current_question": "Tell us about yourself and your work experience",
  "status": "active",
  "answer_text": "",
  "voice_analysis": null,
  "message": "Answer saved successfully"
}

// Subsequent requests
{
  "interview_id": "64f1a2b3c4d5e6f7a8b9c0d7",
  "mlinterview_id": "ai_interview_123",
  "question": "Tell us about yourself and your work experience",
  "answer_text": "I've been working as a Python developer for 3 years...",
  "analysis": {
    "confidence": 0.95,
    "emotions": ["confident", "professional"]
  }
}

// Response on completion (201)
{
  "interview_id": "64f1a2b3c4d5e6f7a8b9c0d7",
  "mlinterview_id": "ai_interview_123",
  "question": "Do you have any questions for us?",
  "current_question": "Do you have any questions for us?",
  "status": "completed",
  "answer_text": "Yes, tell me about the team...",
  "voice_analysis": {...},
  "message": "Answer saved successfully"
}

// Errors: 400 (incomplete data), 500 (AI service error)
```

**GET /interviews/{interview_id}/qna** — Get the interview's questions and answers

```json
// Response (200)
{
  "interview_id": "64f1a2b3c4d5e6f7a8b9c0d7",
  "qna": [
    {
      "_id": "64f1a2b3c4d5e6f7a8b9c0d8",
      "interview_id": "64f1a2b3c4d5e6f7a8b9c0d7",
      "mlinterview_id": "ai_interview_123",
      "question": "Tell us about yourself and your work experience",
      "status": "active",
      "answer_text": "I've been working as a Python developer for 3 years...",
      "voice_analysis": {...},
      "created_at": "2023-09-01T10:00:00Z"
    },
    {
      "_id": "64f1a2b3c4d5e6f7a8b9c0d9",
      "interview_id": "64f1a2b3c4d5e6f7a8b9c0d7",
      "mlinterview_id": "ai_interview_123",
      "question": "How do you test your code?",
      "status": "completed",
      "answer_text": "I use pytest for unit tests...",
      "recommendation": "Recommended for hire",
      "voice_analysis": {...},
      "created_at": "2023-09-01T10:05:00Z"
    }
  ]
}

// Errors: 400 (invalid ID), 403 (no permission), 404 (interview not found)
```

**PUT /interviews/{interview_id}/status** — Change the interview status (owner company only)

```json
// Request
{
  "status": "test_task"
}

// Response (200)
{
  "message": "Interview status successfully changed to \"test_task\""
}

// Errors: 400 (invalid status), 403 (no permission), 404 (interview not found)
```

**PUT /interviews/change-status** — Change the status with a history record (companies only)

```json
// Request
{
  "interview_id": "64f1a2b3c4d5e6f7a8b9c0d7",
  "status": "finalist"
}

// Response (200)
{
  "message": "Interview status updated successfully"
}

// Errors: 400 (incomplete data/invalid status), 404 (interview not found)
```

**GET /vacancies/{vacancy_id}/interviews** — Interviews for a vacancy (owner company)

```json
// Response (200)
{
  "total": 3,
  "page": 1,
  "per_page": 20,
  "total_pages": 1,
  "interviews": [
    {
      "_id": "64f1a2b3c4d5e6f7a8b9c0d7",
      "user_id": "64f1a2b3c4d5e6f7a8b9c0d2",
      "vacancy_id": "64f1a2b3c4d5e6f7a8b9c0d6",
      "status": "completed",
      "resume_score": 85,
      "interview_analysis": "The candidate demonstrated excellent knowledge...",
      "recommendation": "Recommended for hire",
      "created_at": "2023-09-01T10:00:00Z",
      "updated_at": "2023-09-01T15:00:00Z"
    }
  ]
}

// Errors: 400 (invalid parameters), 403 (no permission), 404 (vacancy not found)
```

**DELETE /interviews/{interview_id}** — Delete an interview (owner user only)

```json
// Response (200)
{
  "message": "Interview deleted successfully",
  "deleted_interview_id": "64f1a2b3c4d5e6f7a8b9c0d7",
  "deleted_answers": 5,
  "deleted_status_history": 2
}

// Errors: 403 (no permission), 404 (interview not found), 500 (delete error)
```

#### Interview statuses

- `rejected` — Rejected (low resume score or HR decision)
- `active` — Active (ready to be conducted)
- `completed` — Completed (the user went through all the questions)
- `test_task` — Test task (assigned by HR)
- `finalist` — Finalist (passed the selection)
- `offer` — Job offer

### JWT and roles

- After `POST /login`, use the issued `token` in `Authorization`
- The `token_required` and `roles_required` decorators check access

### Logs

- Request/response and error logging is configured in `app/logging_config.py` and initialized in `app/__init__.py`

### CORS

- All origins are allowed (`CORS(app, origins="*")`), the necessary headers are set automatically

### Building the backend image separately

```
cd backend
docker build -t moretech-backend:latest .
docker run --env-file ../.env -p 5000:5000 moretech-backend:latest
```

### Notes

- For S3 to work, you need a correct configuration of AWS/Yandex keys in the container/process environment
- If S3 is not configured, resumes are saved locally in `uploads/resumes`

## HH.ru API integration

### Integration overview

The MoreTech.VTB platform is integrated with the HeadHunter API to ensure seamless work with the largest Russian job search platform. The integration makes it possible to automate the processes of importing candidate data and to expand profile analysis capabilities.

### Functional capabilities

#### Importing candidate data

| Feature | Description | Technical details |
|---------|----------|-------------------|
| **OAuth authorization** | Secure authorization via HH.ru | OAuth 2.0, refresh tokens |
| **Resume import** | Automatic retrieval of the full resume | REST API, JSON structure |
| **Profile synchronization** | Updating personal data and contacts | Periodic synchronization |
| **Work history** | Importing work experience and achievements | Structured data |
| **Education** | Automatic filling of education data | Validation and normalization |

#### Benefits for candidates

- **Fast registration** — log in via HH.ru in 30 seconds
- **Profile autofill** — eliminates duplicate data entry
- **Change synchronization** — automatic information updates
- **Smart matching** — AI analysis of the HH profile to suggest vacancies
- **Advanced analytics** — additional metrics based on HH data

#### Benefits for employers

- **Expanded candidate base** — access to millions of HH.ru resumes
- **Deep analytics** — analysis of the candidate's activity on the platform
- **Fast screening** — automatic preliminary evaluation
- **Response statistics** — data on candidates' reactions to offers
- **Precise targeting** — search by detailed HH.ru criteria

### Technical implementation

#### API endpoints

```http
# Initiating OAuth authorization
GET /auth/hh/login
Response: Redirect to https://hh.ru/oauth/authorize

# Handling the callback from HH.ru
GET /auth/hh/callback?code=AUTH_CODE
Response: {"token": "jwt_token", "profile_imported": true}

# Synchronizing profile data
POST /api/hh/sync-profile
Authorization: Bearer <token>
Response: {"updated_fields": ["experience", "skills"], "status": "success"}
```

#### Structure of the imported data

```json
{
  "personal_info": {
    "first_name": "Ivan",
    "last_name": "Petrov",
    "email": "ivan.petrov@email.com",
    "phone": "+7 (999) 123-45-67",
    "birth_date": "1990-05-15",
    "location": "Moscow"
  },
  "experience": [
    {
      "company": "Tekhnologii LLC",
      "position": "Senior Python Developer",
      "start_date": "2020-03-01",
      "end_date": null,
      "description": "Developing ML models and web applications",
      "skills": ["Python", "ML", "Docker"]
    }
  ],
  "education": [
    {
      "institution": "MSU",
      "faculty": "CMC",
      "specialization": "Applied Mathematics",
      "year": 2012
    }
  ],
  "skills": ["Python", "Machine Learning", "SQL", "Docker"],
  "salary_expectations": {
    "amount": 200000,
    "currency": "RUR"
  },
  "hh_metrics": {
    "profile_views": 1250,
    "response_rate": 0.75,
    "last_activity": "2024-09-19T15:30:00Z"
  }
}
```

### Integration process

#### For candidates

```
1. Candidate on HH.ru
   ↓
2. OAuth authorization
   ↓
3. Resume import
   ↓
4. AI profile analysis
   ↓
5. Personal recommendations
   ↓
6. Automatic matching
```

#### For HR specialists

```
1. HR specialist
   ↓
2. Candidate search
   ↓
3. Analysis of HH profiles
   ↓
4. AI resume screening
   ↓
5. Forming a short list
   ↓
6. Invitation to an AI interview
```

### Security and privacy

- **OAuth 2.0** — standard authorization without transferring passwords
- **Data encryption** — all personal data is encrypted
- **Expiring tokens** — automatic refresh of access tokens
- **Minimal permissions** — requesting only the necessary data
- **GDPR compliance** — adherence to data protection requirements

### Integration statistics

```
HH.ru integration usage metrics:
├── OAuth authorizations: 2,847
├── Imported resumes: 2,634 (92.5%)
├── Profile synchronizations: 1,892
├── Average import time: 3.2 sec
└── Matching success: +34% with HH data
```

### Integration setup

#### Environment variables

```bash
HH_CLIENT_ID=your_hh_client_id
HH_CLIENT_SECRET=your_hh_client_secret
HH_REDIRECT_URI=https://your-domain.com/auth/hh/callback
```

#### Configuration in code

```python
HH_CONFIG = {
    'client_id': os.getenv('HH_CLIENT_ID'),
    'client_secret': os.getenv('HH_CLIENT_SECRET'),
    'redirect_uri': os.getenv('HH_REDIRECT_URI'),
    'scope': 'read_resume read_profile',
    'api_base_url': 'https://api.hh.ru'
}
```

## Application status system

The platform supports the full application lifecycle with color coding:

| Status | Color | Description |
|--------|------|----------|
| **Active** | Blue | Active applications under review |
| **Completed** | Green | Successfully completed AI interviews |
| **Test Task** | Orange | A test task has been sent |
| **Finalist** | Purple | The candidate is in the final selection |
| **Offer** | Yellow | A job offer has been received |
| **Rejected** | Red | Rejected applications |
