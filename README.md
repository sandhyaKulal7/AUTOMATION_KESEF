# KESEF Portal — Playwright Automation Framework

## Stack
- **Language**: Python 3.11+
- **Framework**: Playwright (sync) + pytest
- **Pattern**: Page Object Model (POM)
- **Reporting**: Allure
- **Data**: Faker + JSON fixtures

## Setup

```bash
# 1. Clone repo and enter directory
cd kesef_automation

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate       # Linux/Mac
venv\Scripts\activate          # Windows

# 3. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 4. Configure environment
cp .env.example .env
# Edit .env and fill in real QA credentials
```

## Running Tests

```bash
# All tests
pytest

# Smoke tests only (fastest — run on every deploy)
pytest -m smoke

# Specific section
pytest tests/test_tc04_fund_deal_calculations.py

# Calculations only (no browser)
pytest -m calculations

# Parallel execution (4 workers)
pytest -n 4

# With Allure report
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```

## Markers
| Marker | When to use |
|---|---|
| `smoke` | Every deploy |
| `sanity` | After a hotfix |
| `regression` | Full regression cycle |
| `calculations` | Pure formula verification — no browser needed |
| `payments` | Payment workflows |
| `reports` | Reports page |
| `cross_screen` | Cross-screen consistency |
| `role_access` | RBAC tests |

## Folder Structure
```
kesef_automation/
├── conftest.py          # Fixtures & browser setup
├── pytest.ini           # Markers & config
├── pages/               # Page Object Model classes
├── tests/               # Test files (one per TC group)
├── utils/
│   ├── calculations.py  # Formula engine (mirrors Kotlin backend)
│   ├── api_client.py    # HTTP client for test data setup
│   ├── data_helpers.py  # Faker-based data factories
│   └── logger.py        # Logging config
└── fixtures/            # JSON test data files
```

## PR Checklist
See `KESEF_PR_Review_Checklist.pdf` for the complete Automation Script Review Checklist.
