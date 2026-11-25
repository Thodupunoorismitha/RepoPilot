# 🚀 RepoPilot
### AI-Powered Codebase Intelligence Platform

RepoPilot is an AI-powered codebase analysis platform designed to help developers understand, explore, and navigate large Python repositories.

It combines **Python AST parsing, dependency graph analysis, code retrieval, and Large Language Models (LLMs)** to provide meaningful insights into code structure and relationships.

Developers can analyze repositories, search for functions, explore dependencies, identify the impact of code changes, and ask natural-language questions about their codebase through an interactive web interface.

## 🎯 Problem Statement

Understanding an unfamiliar or large codebase can be challenging, especially when developers need to:

- Identify where functions and classes are defined.
- Understand how functions interact across multiple files.
- Trace dependencies and discover callers.
- Determine which parts of the codebase may be affected by a change.
- Find relevant implementation details without manually searching through files.

RepoPilot addresses these challenges by automating code analysis and providing an AI-powered interface for codebase exploration.

## ✨ Key Features

- **Repository Analysis:** Recursively scans Python repositories and extracts code structure.
- **AST-Based Parsing:** Identifies functions, classes, methods, imports, parameters, and source line numbers.
- **Dependency Graph:** Builds directed graphs using NetworkX to represent function relationships.
- **Symbol Search:** Finds function definitions across repository files.
- **Caller Analysis:** Identifies functions that call a specified function.
- **Dependency Exploration:** Discovers functions called by a selected function.
- **Impact Analysis:** Identifies direct and indirect callers that may be affected by code changes.
- **Code Retrieval:** Uses TF-IDF and cosine similarity to retrieve relevant code chunks.
- **AI Code Assistant:** Uses Google Gemini with retrieval-augmented generation (RAG) to answer natural-language questions about the codebase.
- **Source References:** Provides relevant file paths and line numbers alongside AI-generated answers.
- **Interactive Dashboard:** Provides a Streamlit interface for repository analysis and code exploration.

## 🛠️ Technology Stack

| Category | Technology | Purpose |
|---|---|---|
| Programming Language | Python 3.15.2 | Core application development |
| Backend Framework | FastAPI | REST API development |
| Frontend Framework | Streamlit | Interactive web dashboard |
| Code Analysis | Python AST | Extracting code structure and metadata |
| Graph Processing | NetworkX | Modeling function dependencies and relationships |
| Database | SQLite | Persistent storage of repositories, symbols, relationships, and code chunks |
| Information Retrieval | Scikit-learn | TF-IDF vectorization and cosine similarity |
| Generative AI | Google Gemini API | Natural-language code understanding and explanations |
| Retrieval Architecture | RAG | Grounding AI responses in retrieved repository code |
| Testing | Pytest | Automated unit and API testing |
| HTTP Client | HTTPX | Communication between frontend and backend |
| Version Control | Git and GitHub | Source code management and collaboration |

## 🏗️ System Architecture

RepoPilot follows a modular architecture that separates code analysis, dependency modeling, persistence, retrieval, AI processing, and user interaction.

### High-Level Workflow

1. **Repository Input:** The developer provides a local Python repository path.
2. **Repository Scanner:** Recursively discovers Python files and handles file-level errors.
3. **AST Parser:** Extracts functions, classes, methods, imports, parameters, and line numbers.
4. **Symbol Table:** Maintains searchable function symbols and their file locations.
5. **Dependency Graph:** Uses NetworkX to model function calls and cross-file relationships.
6. **SQLite Persistence:** Stores repository metadata, symbols, relationships, and code chunks.
7. **Code Retrieval:** Uses TF-IDF and cosine similarity to identify relevant code.
8. **AI Processing:** Combines retrieved code and dependency context to construct a prompt for Google Gemini.
9. **API Layer:** FastAPI exposes analysis and code intelligence endpoints.
10. **Frontend:** Streamlit provides an interactive interface for developers.

### Architecture Diagram

```text
              Python Repository
                      |
                      v
              Repository Scanner
                      |
                      v
                 AST Parser
                      |
             +--------+--------+
             |                 |
             v                 v
         Symbol Table     Code Chunker
             |                 |
             v                 v
       Dependency Graph    TF-IDF Retrieval
             |                 |
             v                 |
          SQLite <-------------+
             |
             v
       Dependency Context
             |
             +--------+
                      |
                      v
                Gemini API
                      |
                      v
                 FastAPI
                      |
                      v
                Streamlit UI
                      |
                      v
             Developer Insights
```

## 🧠 Core Concepts Demonstrated

- Abstract Syntax Trees (AST) for static code analysis.
- Directed graphs and graph traversal algorithms.
- Symbol resolution and cross-file dependency mapping.
- Relational database design and persistence.
- Information retrieval using TF-IDF and cosine similarity.
- Retrieval-Augmented Generation (RAG).
- REST API development and request validation.
- Mocking and automated testing.

## 📁 Project Structure

```text
RepoPilot/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── analyzer/
│   │   ├── parser.py
│   │   ├── scanner.py
│   │   └── service.py
│   │
│   ├── graph/
│   │   ├── dependency_graph.py
│   │   └── symbol_table.py
│   │
│   ├── retrieval/
│   │   ├── chunker.py
│   │   └── retriever.py
│   │
│   ├── ai/
│   │   ├── gemini_client.py
│   │   └── qa_service.py
│   │
│   ├── db/
│   │   ├── database.py
│   │   ├── init_db.py
│   │   ├── repository_db.py
│   │   ├── symbol_db.py
│   │   ├── relationship_db.py
│   │   └── chunk_db.py
│   │
│   └── schemas/
│       ├── analysis.py
│       └── qa.py
│
├── frontend/
│   └── streamlit_app.py
│
├── tests/
│   ├── test_main.py
│   ├── test_api.py
│   ├── test_parser.py
│   ├── test_scanner.py
│   ├── test_symbol_table.py
│   ├── test_dependency_graph.py
│   └── test_retriever.py
│
├── sample_repos/
├── benchmarks/
├── docs/
├── requirements.txt
├── .gitignore
└── README.md
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Thodupunoorismitha/RepoPilot.git

cd RepoPilot
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows CMD:

```cmd
.venv\Scripts\activate.bat
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Gemini API

Create a `.env` file in the project root directory:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.5-flash
```

Replace `your_gemini_api_key` with your own Google Gemini API key.

Keep `.env` private. Never commit API keys to GitHub.

### 5. Initialize the database

```bash
python -m app.db.init_db
```

### 6. Start the FastAPI backend

```bash
uvicorn app.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

### 7. Start the Streamlit frontend

Open a second terminal, activate the virtual environment, navigate to the project directory, and run:

```bash
streamlit run frontend/streamlit_app.py
```

Frontend URL:

```text
http://localhost:8501
```

**Note:** Keep the FastAPI backend running while using the Streamlit frontend.

## 🔌 API Reference

RepoPilot exposes RESTful APIs through FastAPI.

Base URL:

```text
http://127.0.0.1:8000
```

### Available Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Checks API health |
| POST | `/analyze` | Analyzes a Python repository |
| GET | `/symbols?name=login` | Searches for a function |
| GET | `/callers/{name}` | Finds functions that call a function |
| GET | `/dependencies/{name}` | Finds functions called by a function |
| GET | `/impact/{name}` | Identifies direct and indirect callers |
| POST | `/ask` | Answers natural-language questions about the repository |

### 1. Health Check

**Request:**

```http
GET /health
```

**Response:**

```json
{
  "status": "ok",
  "service": "repopilot-api"
}
```

### 2. Analyze Repository

**Request:**

```http
POST /analyze
```

**Request Body:**

```json
{
  "repo_path": "C:/Projects/sample_repository"
}
```

**Example Response:**

```json
{
  "total_files": 3,
  "successful_files": 3,
  "failed_files": 0,
  "repository_id": 3,
  "symbols_saved": 3,
  "relationships_saved": 1,
  "message": "Repository analysis completed"
}
```

### 3. Search Symbols

**Request:**

```http
GET /symbols?name=login
```

Searches for matching function definitions and returns their file paths and source line numbers.

### 4. Find Callers

**Request:**

```http
GET /callers/login
```

Identifies functions that call the specified function.

### 5. Find Dependencies

**Request:**

```http
GET /dependencies/start_application
```

Identifies functions called by the specified function.

### 6. Impact Analysis

**Request:**

```http
GET /impact/login
```

Uses graph traversal to identify direct and indirect callers that may be affected by changes to the specified function.

### 7. AI Code Assistant

**Request:**

```http
POST /ask
```

**Request Body:**

```json
{
  "repository_id": 3,
  "question": "Which login function does start_application call, and why?",
  "top_k": 5
}
```

The API retrieves relevant code chunks, incorporates dependency context, and uses Google Gemini to generate an explanation with source references.

**Example Response:**

```json
{
  "question": "Which login function does start_application call?",
  "answer": "start_application calls login() from auth.py.",
  "sources": [
    {
      "file_path": "sample_repos/graph_demo/auth.py",
      "symbol_name": "login",
      "start_line": 1,
      "end_line": 2,
      "similarity": 0.91
    }
  ]
}
```

*The AI response and source list depend on the repository and question.*

### Interactive API Documentation

Explore and test all available endpoints using Swagger UI:

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## 🧪 Testing and Quality Assurance

RepoPilot uses **Pytest** to validate its core functionality and API behavior.

### Test Coverage

| Test Module | Tests |
|---|---:|
| API | 10 |
| Dependency Graph | 9 |
| Main / Health Check | 1 |
| AST Parser | 10 |
| Code Retriever | 3 |
| Repository Scanner | 4 |
| Symbol Table | 5 |
| **Total** | **42** |

### Testing Highlights

- Validates AST parsing of functions, classes, imports, and methods.
- Tests repository scanning and error handling.
- Verifies dependency graph construction and cross-file relationships.
- Tests symbol lookup and duplicate function names.
- Validates code retrieval and similarity ranking.
- Tests API request validation and error responses.
- Tests AI Q&A success and failure scenarios using mocks, without making real Gemini API calls.

### Run Tests

Execute the complete test suite:

```bash
pytest -v
```

### Latest Test Results

- **Total tests:** 42
- **Passed:** 42
- **Failed:** 0
- **Execution time:** 27.23 seconds

<badge color="success">All 42 automated tests passed</badge>

## 🚀 Future Enhancements

- Support for additional programming languages.
- Improved cross-file and method-level dependency resolution.
- More advanced semantic code retrieval.
- Dependency graph visualization.
- Git-based change impact analysis.
- Repository comparison and analysis history.
- Enhanced AI explanations with more precise source selection.

## 👩‍💻 Author

**Smitha Thodupunoori**

- GitHub: [@Thodupunoorismitha](https://github.com/Thodupunoorismitha)

## 📄 License

This project is developed for learning, experimentation, and portfolio demonstration purposes.