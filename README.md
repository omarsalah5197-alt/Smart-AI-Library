# Smart AI Library 📚

An intelligent web-based library management system that integrates Artificial Intelligence to improve book discovery, recommendations, and student interaction.

## Features

### Student Features
- Student registration and login.
- Browse available books.
- Semantic book search.
- AI-based book recommendations.
- Add and remove favorite books.
- Borrow and return books.
- View borrowing history.
- Interact with the Smart Assistant.

### Admin Features
- Admin dashboard.
- Add, edit, and delete books.
- View student borrowing records.

## AI Components

| Component | Technology |
|---|---|
| Semantic Search | Sentence Transformers |
| Text Embeddings | Multilingual MiniLM |
| Similarity Matching | Cosine Similarity |
| Book Recommendations | TF-IDF |
| Smart Assistant | Semantic Intent Detection |
| Intent Fallback | Keyword-Based Detection |

## Technologies

- Python
- Flask
- MySQL
- HTML, CSS, JavaScript
- Sentence Transformers
- Scikit-learn
- Pytest

## Project Structure

```text
Smart-AI-Library/
├── ai/
├── app/
├── database/
├── data/
├── docs/
├── tests/
├── config.py
├── run.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd Smart-AI-Library
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Configure the Database

- Install and start MySQL.
- Create the project database.
- Configure the database connection settings.
- Set the required environment variables.
- Import the database schema and initial data if provided.

Do not commit database passwords or secret keys.

### 6. Run the Application

```bash
python run.py
```

Open the local address displayed in the terminal.

## Running Tests

Run all tests:

```bash
python -m pytest
```

Generate the coverage report:

```bash
python -m pytest --cov=ai --cov=app --cov=database --cov-report=html
```

## Documentation

Additional project documentation is available in the `docs/` directory.

## Project Purpose

This project demonstrates how Artificial Intelligence can be integrated into a traditional library management system to improve search, recommendations, and user experience.