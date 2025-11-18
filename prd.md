# Product Requirements Document: Code Exercise Grading System

## Executive Summary
A multi-agent Python system that automates the grading workflow for programming assignments by processing Gmail submissions, analyzing code quality, generating personalized feedback, and creating draft responses.

---

## 1. System Architecture Overview

### 1.1 Design Philosophy
Following **Martin Fowler's architectural principles**:
- **Microservices approach**: 4 independent agents with clear boundaries
- **Event-driven**: Status-based workflow coordination
- **Separation of concerns**: Each agent owns its domain
- **Shared-nothing architecture**: Communication via files (Excel as data bus)
- **Plugin architecture**: Agents can run independently or orchestrated

### 1.2 Clean Code Principles (Uncle Bob)
- **Single Responsibility**: Each agent does ONE thing
- **Maximum file length**: 150 lines per file (strict)
- **No duplication**: Shared utilities extracted to common modules
- **Dependency Inversion**: Agents depend on abstractions (interfaces)
- **Open/Closed**: Easy to add new agents without modifying existing ones

---

## 2. Agent Specifications

### Agent 1: Email Collector
**Responsibility**: Gmail integration and submission extraction

**Inputs**:
- Gmail account: `edialagerlov1@gmail.com` (configurable)
- Folder: `AICourse2025` (configurable)
- Subject filter: "בדיקה עצמית של תרגיל" (configurable)

**Outputs**:
- File: `ExcelBK_byAgent1.xlsx`
- Columns: `ID`, `Date`, `email`, `subject`, `Repo`, `Status`
- Status values: `ready` when completed

**Technical Requirements** (Kenneth Reitz API Design):
- Gmail API client with OAuth2 authentication
- Sensible defaults, configurable via kwargs
- Context manager for API session handling
- Clear error messages for auth failures
- Retry logic with exponential backoff
- URL extraction via regex patterns

**Data Handling** (Wes McKinney):
- Use `pandas.DataFrame` for in-memory operations
- Export with `df.to_excel()` using `openpyxl` engine
- Proper dtype specification: `ID` (int), `Date` (datetime64)
- Atomic writes (temp file + rename)

**Logging**:
- File: `agent1.log`
- Max lines: 2000 (cyclic/rotating)
- Format: `timestamp | level | message`

---

### Agent 2: Code Analyzer
**Responsibility**: Repository cloning and code quality scoring

**Inputs**:
- File: `ExcelBK_byAgent1.xlsx`
- Filter: `Status == 'ready'`

**Outputs**:
- File: `Grade_byAgent2.xlsx`
- Columns: `ID`, `grade`, `Status`
- Status values: `ready` when completed

**Grading Algorithm**:
```
score = (lines_in_files_≤150 / total_python_lines) * 100
```

**Technical Requirements** (David Beazley Concurrency):
- Multi-threaded processing using `ThreadPoolExecutor`
- Thread-safe queue for work distribution
- Worker threads: configurable (default: 4)
- Git operations: `subprocess` with proper error handling
- Temporary directories: `tempfile.mkdtemp()` per thread
- Cleanup: `shutil.rmtree()` in finally blocks
- Thread-local storage for per-thread state
- Graceful shutdown on SIGTERM/SIGINT

**Code Analysis** (Guido's Python Approach):
- AST parsing for accurate line counting
- Exclude: comments, docstrings, blank lines
- Use `pathlib.Path` for file operations
- Generator expressions for file iteration
- Type hints throughout

**Logging**:
- File: `agent2.log`
- Thread-safe logging with `logging.handlers.RotatingFileHandler`
- Max lines: 2000

---

### Agent 3: AI Feedback Generator
**Responsibility**: LLM-based personalized feedback generation

**Inputs**:
- File: `Grade_byAgent2.xlsx`
- Filter: `Status == 'ready'`

**Outputs**:
- File: `Feedback_ByAgent3.xlsx`
- Columns: `ID`, `Feedback`, `Status`
- Status values: `ready` when completed

**Feedback Rules**:
| Grade Range | Style | Skill File |
|-------------|-------|------------|
| 0-55 | Donald Trump | `/trump-feedback` |
| 55-70 | Shachar Hason | `/shachar-feedback` |
| 70-90 | Improvement expectation | Standard template |
| 90-100 | Dudi Amsalem | `/dudi-feedback` |

**Technical Requirements** (Kenneth Reitz + Uncle Bob):
- Strategy Pattern for feedback generation
- Interface: `FeedbackGenerator` protocol
- Implementations: `TrumpFeedback`, `ShacharFeedback`, `DudiFeedback`, `StandardFeedback`
- LLM client: Anthropic Claude API (configurable)
- Prompt templates: External files (`.skill` integration)
- Rate limiting: Token bucket algorithm
- Retry logic: 3 attempts with backoff

**Architecture** (Martin Fowler):
```
FeedbackService
  ├── FeedbackStrategyFactory
  ├── LLMClient (abstraction)
  │   └── ClaudeClient (implementation)
  └── PromptTemplateLoader
```

**Logging**:
- File: `agent3.log`
- Max lines: 2000
- Include: LLM tokens used, costs

---

### Agent 4: Email Drafter
**Responsibility**: Draft email composition in Gmail

**Inputs**:
- File: `Feedback_ByAgent3.xlsx` (for feedback)
- File: `ExcelBK_byAgent1.xlsx` (for recipient emails)
- Join key: `ID`
- Filter: `Status == 'ready'`

**Outputs**:
- Gmail draft emails (one per submission)

**Technical Requirements** (Guido + Kenneth):
- Gmail API: `drafts.create()` method
- Join DataFrames using `pandas.merge()`
- Email template: HTML with embedded feedback
- Batch API requests: `batch()` executor
- OAuth2 scope: `gmail.compose`

**Email Template**:
```html
Subject: תוצאות בדיקה עצמית - תרגיל
Body:
  שלום,

  {feedback_text}

  בברכה,
  המערכת
```

**Logging**:
- File: `agent4.log`
- Max lines: 2000

---

## 3. Package Structure (Uncle Bob + Martin Fowler)

```
code_grading_system/
├── pyproject.toml
├── README.md
├── .env.example
├── requirements.txt
├── src/
│   └── code_grading/
│       ├── __init__.py
│       ├── __main__.py          # CLI entry point
│       ├── config.py            # Configuration management (< 150 lines)
│       ├── common/
│       │   ├── __init__.py
│       │   ├── logging.py       # Cyclic logger (< 150 lines)
│       │   ├── excel_handler.py # Pandas operations (< 150 lines)
│       │   └── status.py        # Status enum/constants (< 150 lines)
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── base.py          # AbstractAgent class (< 150 lines)
│       │   ├── agent1/
│       │   │   ├── __init__.py
│       │   │   ├── gmail_client.py   (< 150 lines)
│       │   │   ├── email_parser.py   (< 150 lines)
│       │   │   └── runner.py         (< 150 lines)
│       │   ├── agent2/
│       │   │   ├── __init__.py
│       │   │   ├── git_client.py     (< 150 lines)
│       │   │   ├── code_analyzer.py  (< 150 lines)
│       │   │   ├── worker.py         (< 150 lines)
│       │   │   └── runner.py         (< 150 lines)
│       │   ├── agent3/
│       │   │   ├── __init__.py
│       │   │   ├── feedback_strategy.py  (< 150 lines)
│       │   │   ├── llm_client.py         (< 150 lines)
│       │   │   ├── template_loader.py    (< 150 lines)
│       │   │   └── runner.py             (< 150 lines)
│       │   └── agent4/
│       │       ├── __init__.py
│       │       ├── gmail_drafter.py  (< 150 lines)
│       │       ├── email_builder.py  (< 150 lines)
│       │       └── runner.py         (< 150 lines)
│       ├── orchestrator/
│       │   ├── __init__.py
│       │   └── pipeline.py      # Run all agents (< 150 lines)
│       └── cli/
│           ├── __init__.py
│           └── commands.py      # Click/argparse CLI (< 150 lines)
├── data/                        # Excel files, logs (gitignored)
├── templates/
│   ├── email_template.html
│   └── prompts/
│       ├── trump.txt
│       ├── shachar.txt
│       └── dudi.txt
└── tests/
    ├── unit/
    ├── integration/
    └── conftest.py
```

**File Count Enforcement**:
- Pre-commit hook: Check line count < 150
- CI/CD gate: Fail if any file > 150 lines

---

## 4. Common Modules (DRY Principle)

### 4.1 Logging Module (`common/logging.py`)
**Pythonic Design** (Guido):
```python
from typing import Protocol
from logging.handlers import RotatingFileHandler

class CyclicLogger(Protocol):
    def setup(log_file: str, max_lines: int = 2000) -> logging.Logger:
        """Create rotating file handler limited to max_lines."""
        ...
```

**Features**:
- Automatic line-based rotation
- Thread-safe
- Structured logging (JSON option)
- Configurable format

### 4.2 Excel Handler (`common/excel_handler.py`)
**Data-First** (Wes McKinney):
```python
from pathlib import Path
import pandas as pd
from typing import List

class ExcelHandler:
    @staticmethod
    def read_with_status(file: Path, status: str) -> pd.DataFrame:
        """Read Excel and filter by status column."""
        df = pd.read_excel(file, engine='openpyxl')
        return df[df['Status'] == status].copy()

    @staticmethod
    def atomic_write(df: pd.DataFrame, file: Path) -> None:
        """Write DataFrame atomically (temp + rename)."""
        ...
```

### 4.3 Base Agent (`agents/base.py`)
**Clean Architecture** (Uncle Bob + Martin Fowler):
```python
from abc import ABC, abstractmethod
from pathlib import Path

class AbstractAgent(ABC):
    def __init__(self, config: dict):
        self.config = config
        self.logger = self._setup_logger()

    @abstractmethod
    def run(self) -> None:
        """Execute agent's main task."""
        pass

    def _setup_logger(self) -> logging.Logger:
        """Setup cyclic logger."""
        pass
```

---

## 5. Configuration Management

**External Configuration** (Martin Fowler):
- File: `.env` for secrets
- File: `config.yaml` for parameters
- Environment variable override support

**Example `.env`**:
```
GMAIL_CREDENTIALS_PATH=./credentials.json
GMAIL_ACCOUNT=edialagerlov1@gmail.com
GMAIL_FOLDER=AICourse2025
SUBJECT_FILTER=בדיקה עצמית של תרגיל
ANTHROPIC_API_KEY=sk-...
WORKER_THREADS=4
```

**Config Loading** (Guido):
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    gmail_account: str
    gmail_folder: str
    subject_filter: str
    worker_threads: int = 4

    @classmethod
    def from_env(cls) -> 'Config':
        """Load from environment variables."""
        ...
```

---

## 6. CLI Interface (Kenneth Reitz Style)

**User-Friendly Commands**:
```bash
# Run individual agents
code-grading agent1
code-grading agent2
code-grading agent3
code-grading agent4

# Run all agents (orchestrated)
code-grading run-all

# Run with custom config
code-grading agent1 --config custom.yaml

# Verbose logging
code-grading run-all --verbose
```

**Implementation** (using Click):
```python
import click

@click.group()
def cli():
    """Code Exercise Grading System"""
    pass

@cli.command()
@click.option('--config', type=click.Path(), help='Config file path')
def agent1(config):
    """Run Email Collector agent"""
    ...

@cli.command()
def run_all():
    """Run all agents in sequence"""
    ...
```

---

## 7. Concurrency Design (David Beazley)

### Agent 2 Multi-Threading Architecture

**Worker Pattern**:
```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
import threading

class CodeAnalyzer:
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.results = Queue()
        self.lock = threading.Lock()

    def analyze_repos(self, repos: List[dict]) -> List[dict]:
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._analyze_one, repo): repo
                for repo in repos
            }

            for future in as_completed(futures):
                try:
                    result = future.result()
                    self.results.put(result)
                except Exception as e:
                    self.logger.error(f"Worker failed: {e}")

        return list(self.results.queue)

    def _analyze_one(self, repo: dict) -> dict:
        """Thread worker: clone, analyze, cleanup."""
        temp_dir = tempfile.mkdtemp()
        try:
            # Clone repo
            # Analyze Python files
            # Calculate score
            return {"id": repo["ID"], "grade": score}
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
```

**Thread Safety**:
- No shared mutable state
- Results collected via thread-safe Queue
- Lock only for critical sections (logging aggregation)
- Thread-local temp directories

---

## 8. Data Flow (Wes McKinney)

### Pandas Operations Best Practices

**Agent 1 → Agent 2**:
```python
# Agent 1: Write
df = pd.DataFrame({
    'ID': range(1, n+1),
    'Date': pd.to_datetime(dates),
    'email': emails,
    'subject': subjects,
    'Repo': repos,
    'Status': 'ready'
})
df.to_excel('ExcelBK_byAgent1.xlsx', index=False, engine='openpyxl')

# Agent 2: Read + Filter
df_input = pd.read_excel('ExcelBK_byAgent1.xlsx', engine='openpyxl')
repos_to_process = df_input[df_input['Status'] == 'ready'].to_dict('records')

# Agent 2: Write Results
df_grades = pd.DataFrame(results)  # results from threads
df_grades.to_excel('Grade_byAgent2.xlsx', index=False)
```

**Agent 3 & 4: Join Data**:
```python
# Agent 4: Join feedback with emails
df_feedback = pd.read_excel('Feedback_ByAgent3.xlsx')
df_emails = pd.read_excel('ExcelBK_byAgent1.xlsx')

df_merged = df_feedback.merge(
    df_emails[['ID', 'email']],
    on='ID',
    how='inner'
)

for _, row in df_merged.iterrows():  # Only when necessary!
    create_draft(row['email'], row['Feedback'])
```

**Optimization**:
- Avoid `iterrows()` when possible (use vectorized ops)
- Specify dtypes on read: `dtype={'ID': int}`
- Use `chunksize` for very large files
- Memory-efficient: Read only needed columns

---

## 9. Error Handling & Resilience

**Pythonic Error Handling** (Guido):
```python
class GradingSystemError(Exception):
    """Base exception for grading system"""
    pass

class GmailAuthError(GradingSystemError):
    """Gmail authentication failed"""
    pass

class RepoCloneError(GradingSystemError):
    """Failed to clone repository"""
    pass
```

**Retry Logic**:
```python
import time
from functools import wraps

def retry(max_attempts=3, backoff=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(backoff ** attempt)
            return None
        return wrapper
    return decorator
```

**Agent-Level Error Handling**:
- Log all errors
- Update status to `error` in Excel
- Continue processing other items
- Send alert email on critical failures

---

## 10. Testing Strategy

### Test Pyramid
**Unit Tests** (Uncle Bob):
- Each function/class tested independently
- Mock external dependencies (Gmail API, LLM API)
- Test edge cases (empty repos, malformed emails)
- Coverage target: 80%+

**Integration Tests** (Martin Fowler):
- Test agent end-to-end with test data
- Use test Gmail account
- Test Excel file I/O
- Test multi-threading behavior

**Test Fixtures**:
```python
# tests/conftest.py
import pytest
import pandas as pd

@pytest.fixture
def sample_excel_data():
    return pd.DataFrame({
        'ID': [1, 2, 3],
        'Repo': ['https://github.com/user/repo1', ...],
        'Status': ['ready', 'ready', 'pending']
    })

@pytest.fixture
def mock_gmail_client(mocker):
    return mocker.patch('code_grading.agents.agent1.gmail_client.GmailClient')
```

---

## 11. Deployment & Operations

### Installation
```bash
# From PyPI (future)
pip install code-grading-system

# From source
git clone <repo>
cd code-grading-system
pip install -e .
```

### Setup
```bash
# 1. Configure credentials
cp .env.example .env
# Edit .env with your values

# 2. Setup Gmail OAuth
code-grading setup-gmail

# 3. Verify installation
code-grading --version
```

### Running in Production
```bash
# Cron job for automated runs
0 */6 * * * /usr/bin/code-grading run-all >> /var/log/grading.log 2>&1

# Docker container
docker run -v ./data:/app/data grading-system:latest run-all

# Systemd service
systemctl start code-grading.service
```

---

## 12. Performance Requirements

**Agent 1** (Email Collector):
- Process 100 emails: < 2 minutes
- Gmail API quota: 250 quota units/user/second

**Agent 2** (Code Analyzer):
- Process 50 repos (4 threads): < 10 minutes
- Temp storage: ~500MB peak
- Network: Git clone bandwidth

**Agent 3** (AI Feedback):
- Process 50 feedbacks: < 5 minutes
- LLM API: Rate limit aware
- Cost: ~$0.02 per feedback (estimate)

**Agent 4** (Email Drafter):
- Create 50 drafts: < 1 minute
- Gmail API: Batch requests

**Total Pipeline**: < 20 minutes for 50 submissions

---

## 13. Security Considerations

**Credentials**:
- OAuth2 tokens stored securely (system keyring)
- Never commit `.env` or credentials to git
- Rotate API keys quarterly

**Data Privacy**:
- Student emails: PII - handle per GDPR
- Temp directories: Cleaned after use
- Logs: Anonymize email addresses

**API Security**:
- HTTPS only
- Token refresh handling
- Scope limitation (minimal permissions)

---

## 14. Monitoring & Observability

**Metrics**:
- Emails processed per run
- Repos analyzed successfully
- LLM tokens consumed
- Drafts created
- Error rate by agent

**Logging Aggregation**:
- All logs: Structured JSON
- Centralized: ELK/CloudWatch (optional)
- Alerts: Email on error rate > 10%

**Dashboard** (future):
- Processing status visualization
- Cost tracking (LLM usage)
- Performance trends

---

## 15. Future Enhancements

**Phase 2**:
- Web UI for manual review
- Student-facing portal to view feedback
- Plagiarism detection (Agent 2.5)
- More feedback styles (add skills)
- Support for other languages (Java, JS)

**Phase 3**:
- Real-time processing (webhook-triggered)
- Advanced code metrics (cyclomatic complexity)
- Auto-reply option (Agent 4 enhancement)
- Integration with LMS platforms

---

## 16. Success Metrics

**Efficiency**:
- Time saved vs manual grading: > 90%
- Processing time per submission: < 2 minutes

**Quality**:
- Instructor satisfaction with feedback: > 80%
- Student satisfaction: > 70%
- Error rate: < 5%

**Adoption**:
- Successfully process 200+ submissions in first semester
- Zero manual intervention required for 80% of runs

---

## Appendix A: Design Patterns Used

| Pattern | Location | Purpose |
|---------|----------|---------|
| Strategy | Agent 3 feedback | Interchangeable feedback styles |
| Factory | Agent 3 | Create appropriate feedback generator |
| Template Method | Base Agent | Common agent lifecycle |
| Repository | Excel Handler | Data access abstraction |
| Singleton | Config | Single config instance |
| Observer | Future: webhooks | React to Gmail events |
| Facade | CLI | Simple interface to complex system |

---

## Appendix B: SOLID Compliance

✅ **Single Responsibility**: Each agent, class, function - one job
✅ **Open/Closed**: Add new feedback styles without modifying existing code
✅ **Liskov Substitution**: All feedback generators interchangeable
✅ **Interface Segregation**: Specific interfaces (GmailReader, RepoAnalyzer)
✅ **Dependency Inversion**: Depend on protocols, not concrete implementations

---

**Document Version**: 1.0
**Last Updated**: 2025-11-17
**Authors**: Synthesized from Guido van Rossum, David Beazley, Wes McKinney, Robert C. Martin, Martin Fowler, Kenneth Reitz principles
