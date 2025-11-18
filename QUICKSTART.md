# Quick Start Guide

## Project Structure

```
code-grading-system/
├── src/code_grading/           # Main package
│   ├── __init__.py
│   ├── __main__.py             # Entry point
│   ├── config.py               # Configuration management
│   ├── common/                 # Shared utilities
│   │   ├── logging.py          # Cyclic logger (max 2000 lines)
│   │   ├── excel_handler.py    # Excel operations with pandas
│   │   └── status.py           # Status constants
│   ├── agents/
│   │   ├── base.py             # Abstract base agent
│   │   ├── agent1/             # Email Collector
│   │   │   ├── gmail_client.py
│   │   │   ├── email_parser.py
│   │   │   └── runner.py
│   │   ├── agent2/             # Code Analyzer (Multi-threaded)
│   │   │   ├── git_client.py
│   │   │   ├── code_analyzer.py
│   │   │   ├── worker.py
│   │   │   └── runner.py
│   │   ├── agent3/             # AI Feedback Generator
│   │   │   ├── llm_client.py
│   │   │   ├── feedback_strategy.py
│   │   │   ├── template_loader.py
│   │   │   └── runner.py
│   │   └── agent4/             # Email Drafter
│   │       ├── gmail_drafter.py
│   │       ├── email_builder.py
│   │       └── runner.py
│   ├── orchestrator/           # Run all agents
│   │   └── pipeline.py
│   └── cli/                    # Command-line interface
│       └── commands.py
├── templates/
│   ├── prompts/                # LLM prompt templates
│   │   ├── trump.txt
│   │   ├── shachar.txt
│   │   ├── dudi.txt
│   │   └── standard.txt
│   └── email_template.html
├── data/                       # Created at runtime (gitignored)
├── tests/
│   └── conftest.py
├── pyproject.toml              # Package configuration
├── requirements.txt
├── .env.example                # Example environment variables
└── README.md
```

## Installation

### 1. Navigate to the project

```bash
cd code-grading-system
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install the package

```bash
pip install -e .
```

Or install dependencies directly:

```bash
pip install -r requirements.txt
```

## Configuration

### 1. Create .env file

```bash
cp .env.example .env
```

### 2. Edit .env with your settings

```bash
# Gmail Configuration
GMAIL_CREDENTIALS_PATH=./credentials.json
GMAIL_TOKEN_PATH=./token.json
GMAIL_ACCOUNT=edialagerlov1@gmail.com
GMAIL_FOLDER=AICourse2025
SUBJECT_FILTER=בדיקה עצמית של תרגיל

# Anthropic AI Configuration
ANTHROPIC_API_KEY=your-api-key-here

# Agent 2 Configuration
WORKER_THREADS=4

# Paths are relative to project root
DATA_DIR=./data
LOG_DIR=./data/logs
```

### 3. Setup Gmail OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download credentials as `credentials.json` in project root

### 4. Setup Anthropic API

1. Get API key from [Anthropic Console](https://console.anthropic.com/)
2. Add to `.env`: `ANTHROPIC_API_KEY=sk-ant-...`

## Usage

### Run Individual Agents

```bash
# Agent 1: Collect emails from Gmail
code-grading agent1

# Agent 2: Analyze code repositories
code-grading agent2

# Agent 3: Generate AI feedback
code-grading agent3

# Agent 4: Create Gmail drafts
code-grading agent4
```

### Run All Agents (Pipeline)

```bash
# Standard run
code-grading run-all

# Verbose mode
code-grading run-all --verbose
```

### Using Python Module

```bash
python -m code_grading agent1
python -m code_grading run-all
```

## Data Flow

```
Gmail Inbox
    ↓
[Agent 1] → ExcelBK_byAgent1.xlsx (ID, Date, email, subject, Repo, Status)
    ↓
[Agent 2] → Grade_byAgent2.xlsx (ID, grade, Status)
    ↓
[Agent 3] → Feedback_ByAgent3.xlsx (ID, Feedback, Status)
    ↓
[Agent 4] → Gmail Drafts
```

## Feedback Styles by Grade

| Grade Range | Style | File |
|-------------|-------|------|
| 0-55 | Donald Trump | `templates/prompts/trump.txt` |
| 55-70 | Shachar Hason | `templates/prompts/shachar.txt` |
| 70-90 | Standard | `templates/prompts/standard.txt` |
| 90-100 | Dudi Amsalem | `templates/prompts/dudi.txt` |

## Logs

All agents maintain cyclic logs (max 2000 lines) in `data/logs/`:
- `agent1.log`
- `agent2.log`
- `agent3.log`
- `agent4.log`

## Development

### Run Tests

```bash
pip install -e ".[dev]"
pytest
pytest --cov=code_grading --cov-report=html
```

### Code Quality

```bash
# Format code
black src/

# Lint
ruff check src/

# Type check
mypy src/
```

## Key Design Principles

✅ **Maximum file length**: 150 lines per file (strict)
✅ **Single Responsibility**: Each file/class does ONE thing
✅ **Relative paths**: All paths relative to project root
✅ **SOLID principles**: Clean architecture throughout
✅ **Type hints**: Full type coverage
✅ **Thread-safe**: Multi-threaded Agent 2
✅ **Strategy Pattern**: Feedback generation
✅ **Dependency Injection**: Agents depend on Config

## Troubleshooting

### Gmail Authentication Issues

```bash
# Remove old token
rm token.json
# Run agent again to re-authenticate
code-grading agent1
```

### Missing Dependencies

```bash
pip install -r requirements.txt
```

### Permission Errors

Ensure `data/` directory is writable:
```bash
mkdir -p data/logs
chmod -R 755 data/
```

## Next Steps

1. Configure `.env` with your credentials
2. Run `code-grading agent1` to test Gmail connection
3. Create test repository and run full pipeline
4. Customize prompt templates in `templates/prompts/`
5. Modify email template in `templates/email_template.html`

---

**Support**: See README.md for more details
**License**: MIT
