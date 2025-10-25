# Complete Testing & Running Guide

Comprehensive guide for testing, running, and maintaining the VirtualClone application.

## Table of Contents
- [Testing](#testing)
  - [Quick Test](#quick-test)
  - [Test Suite Overview](#test-suite-overview)
  - [Running Tests](#running-tests)
  - [Test Coverage](#test-coverage)
- [Running the Application](#running-the-application)
  - [Development Mode](#development-mode)
  - [Production Mode](#production-mode)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)

---

## Testing

### Quick Test

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests
pytest -q

# Expected: 57 passed in ~2-3 seconds
```

### Test Suite Overview

**Total Tests**: 57 across 6 test files

| Test File | Tests | Coverage |
|-----------|-------|----------|
| `test_ai_service.py` | 16 | AI service, caching, similarity |
| `test_app.py` | 5 | Flask app setup, blueprints |
| `test_config.py` | 5 | Configuration validation |
| `test_context_loader.py` | 3 | Context file loading |
| `test_file_service.py` | 18 | File uploads, validation |
| `test_main_routes.py` | 10 | API routes, integration |

### Running Tests

#### Basic Commands

```bash
# All tests (quiet)
pytest -q

# All tests (verbose)
pytest -v

# Specific test file
pytest tests/test_ai_service.py

# Specific test class
pytest tests/test_ai_service.py::TestAIService

# Specific test method
pytest tests/test_ai_service.py::TestAIService::test_cache_initialization

# Tests matching pattern
pytest -k "translation"

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l
```

#### Advanced Testing

```bash
# Parallel execution (faster)
pip install pytest-xdist
pytest -n 4

# Watch mode (auto-run on changes)
pip install pytest-watch
ptw

# With coverage report
pytest --cov=app --cov-report=term-missing

# HTML coverage report
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

### Test Coverage

Current coverage: **~85%**

```bash
# Generate coverage report
pytest --cov=app --cov-report=term-missing

# View detailed HTML report
pytest --cov=app --cov-report=html
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

Coverage by module:
- `app/config.py`: 100%
- `app/services/ai_service.py`: 92%
- `app/services/file_service.py`: 91%
- `app/routes/main_routes.py`: 87%

---

## Running the Application

### Development Mode

#### 1. Setup (First Time Only)

```bash
# Clone repository
git clone https://github.com/kh3rld/VirtualClone.git
cd VirtualClone

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env

# Edit .env if needed
nano .env
```

#### 2. Start Development Server

```bash
# Activate virtual environment (if not already)
source .venv/bin/activate

# Start Flask development server
python run.py
```

Output should show:
```
[INFO] AI Service initialized (models will load on first use)
[INFO] Flask application starting...
[INFO] Registered blueprints: ['upload', 'main', 'links', 'api']
[INFO] Starting server on 0.0.0.0:5050 (debug=True)
 * Running on http://0.0.0.0:5050
```

#### 3. Access the Application

- **Web UI**: http://localhost:5050
- **API Health Check**: http://localhost:5050/hello
- **API v1**: http://localhost:5050/api/v1
- **Upload Page**: http://localhost:5050/upload
- **Links Page**: http://localhost:5050/links

#### 4. Test the Application

```bash
# Test health endpoint
curl http://localhost:5050/hello

# Test question answering (example)
curl -X POST http://localhost:5050/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "user_input=What is artificial intelligence?"
```

### Production Mode

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete production deployment guide.

#### Quick Production Start

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn (4 workers)
gunicorn -w 4 -b 0.0.0.0:5050 --timeout 120 run:app

# Or with logging
gunicorn -w 4 -b 0.0.0.0:5050 --timeout 120 \
  --access-logfile access.log \
  --error-logfile error.log \
  run:app
```

**Important**: Set these in production `.env`:
```bash
FLASK_ENV=production
FLASK_DEBUG=False
FLASK_SECRET_KEY=<generate-secure-key>
```

Generate secure key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## API Documentation

### Main Endpoints

#### 1. Home / Question Answering
```http
POST /
Content-Type: application/x-www-form-urlencoded

user_input=What is AI?
language=eng_Latn

Response:
{
  "user_input": "What is AI?",
  "answer": "Artificial Intelligence is...",
  "selected_language": "eng_Latn"
}
```

#### 2. Health Check
```http
GET /hello

Response:
"Hello, World! The server is running."
```

#### 3. Session Reset
```http
GET /reset

Response:
"Session cleared"
```

#### 4. Language Selection
```http
POST /
Content-Type: application/x-www-form-urlencoded

language=spa_Latn

Response:
{
  "message": "Language selected",
  "selected_language": "spa_Latn"
}
```

### API v1 (RESTful)

#### Chat Endpoint
```http
POST /api/v1/chat
Content-Type: application/json

{
  "question": "What is machine learning?",
  "language": "eng_Latn"
}

Response:
{
  "question": "What is machine learning?",
  "answer": "Machine learning is...",
  "language": "eng_Latn",
  "timestamp": "2025-10-25T12:34:56Z"
}
```

### Upload Endpoints

#### File Upload
```http
POST /upload/
Content-Type: multipart/form-data

file: <video file>

Response:
HTML page with transcript
```

#### Video Link Processing
```http
POST /links/
Content-Type: application/x-www-form-urlencoded

url=https://youtube.com/watch?v=example

Response:
HTML page with transcript
```

---

## Configuration

### Environment Variables

Edit `.env` to configure:

```bash
# Flask Settings
FLASK_SECRET_KEY=your-secret-key-change-in-production
FLASK_DEBUG=True
FLASK_PORT=5050

# AI Models
AI_MODEL_TRANSLATION=facebook/nllb-200-distilled-600M
AI_MODEL_QA=deepset/roberta-base-squad2
WHISPER_MODEL=tiny

# AI Behavior (NEW - Production Ready!)
AI_QA_TOP_K_PRIMARY=3
AI_QA_TOP_K_DIVERSE=5
AI_MAX_ANSWER_LEN=150
CONVERSATION_RECENT_EXCHANGES=3
REPETITION_HISTORY_WINDOW=5
REPETITION_SIMILARITY_THRESHOLD=0.7

# Upload Settings
MAX_CONTENT_LENGTH=31457280
ALLOWED_EXTENSIONS=mp4,mov,avi,mkv

# Logging
LOG_LEVEL=INFO
LOG_FILE=app.log
```

### Model Configuration

**Development** (faster, less accurate):
```bash
WHISPER_MODEL=tiny
AI_MODEL_QA=distilbert-base-cased-distilled-squad
```

**Production** (slower, more accurate):
```bash
WHISPER_MODEL=base
AI_MODEL_QA=deepset/roberta-base-squad2
```

### GPU Acceleration

The app automatically detects and uses NVIDIA GPU if available:

```bash
# Check GPU availability
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# Install CUDA-enabled PyTorch (if needed)
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

---

## Troubleshooting

### Tests Failing

#### Problem: Import errors
```bash
ModuleNotFoundError: No module named 'flask'
```

**Solution**:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

#### Problem: Tests not discovered
```bash
collected 0 items
```

**Solution**:
```bash
# Ensure you're in project root
cd /path/to/VirtualClone

# Run from root
pytest

# Check pytest.ini is present
cat pytest.ini
```

#### Problem: Specific test fails
```bash
# Run with verbose output
pytest -vv tests/test_ai_service.py

# Show local variables
pytest -l tests/test_ai_service.py

# Enter debugger
pytest --pdb tests/test_ai_service.py
```

### Application Issues

#### Problem: Port already in use
```bash
Address already in use: Port 5050
```

**Solution**:
```bash
# Find process using port
lsof -i :5050  # Linux/macOS
netstat -ano | findstr :5050  # Windows

# Kill process or change port in .env
FLASK_PORT=5051
```

#### Problem: Models not loading
```bash
# Download models manually
python -c "from transformers import pipeline; pipeline('translation', model='facebook/nllb-200-distilled-600M')"
```

#### Problem: FFmpeg not found
```bash
# Install FFmpeg
sudo apt install ffmpeg  # Ubuntu
brew install ffmpeg  # macOS
```

### Performance Issues

#### Slow first request
This is normal - models load on first use. Subsequent requests are fast.

#### Out of memory
```bash
# Use smaller models
WHISPER_MODEL=tiny
AI_MODEL_QA=distilbert-base-cased-distilled-squad

# Or increase system RAM/swap
```

#### Slow responses
```bash
# Enable GPU if available
python -c "import torch; print(torch.cuda.is_available())"

# Adjust AI settings in .env
AI_MAX_ANSWER_LEN=100  # Shorter answers
AI_QA_TOP_K_PRIMARY=2  # Fewer candidates
```

---

## Development Workflow

### Typical Development Session

```bash
# 1. Start session
cd VirtualClone
source .venv/bin/activate

# 2. Pull latest changes
git pull origin main

# 3. Install any new dependencies
pip install -r requirements.txt

# 4. Run tests
pytest -q

# 5. Start development server
python run.py

# 6. Make changes...

# 7. Test changes
pytest

# 8. Commit and push
git add .
git commit -m "Description of changes"
git push origin feature-branch
```

### Before Committing

```bash
# 1. Run all tests
pytest

# 2. Check coverage
pytest --cov=app --cov-report=term-missing

# 3. Format code (optional)
pip install black
black app/ tests/

# 4. Check for issues
pip install flake8
flake8 app/ tests/ --max-line-length=100

# 5. Verify app starts
python run.py
# Ctrl+C to stop

# 6. Commit
git add .
git commit -m "Your message"
```

---

## Quick Reference

### Essential Commands

```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Test
pytest -q                           # Run all tests
pytest --cov=app --cov-report=html  # With coverage
pytest -k "test_name"                # Specific test

# Run
python run.py                        # Development
gunicorn -w 4 -b 0.0.0.0:5050 run:app  # Production

# Check
curl http://localhost:5050/hello     # Health check
tail -f app.log                      # View logs
```

### File Locations

```
VirtualClone/
├── .env                   # Configuration (create from .env.example)
├── run.py                 # Application entry point
├── pytest.ini             # Test configuration
├── requirements.txt       # Python dependencies
├── app.log               # Application logs
├── app/                  # Application code
│   ├── __init__.py       # App factory
│   ├── config.py         # Configuration
│   ├── routes/           # API endpoints
│   ├── services/         # Business logic
│   └── static/           # CSS/JS
├── tests/                # Test suite
├── uploads/              # User uploads
└── downloads/            # Downloaded content
```

---

## Getting Help

1. **Check logs**: `tail -f app.log`
2. **Run tests**: `pytest -vv`
3. **Check configuration**: `cat .env`
4. **View documentation**:
   - [SETUP.md](SETUP.md) - Setup guide
   - [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment
   - [README.md](README.md) - Project overview

5. **GitHub Issues**: https://github.com/kh3rld/VirtualClone/issues

---

## Summary

✅ **Setup complete** if:
- Virtual environment created and activated
- Dependencies installed
- `.env` file configured
- Tests pass: `pytest -q`

✅ **Ready to develop** if:
- App starts: `python run.py`
- Health check works: `curl http://localhost:5050/hello`
- Tests pass after changes

✅ **Ready for production** if:
- All tests pass
- Coverage > 80%
- `FLASK_DEBUG=False`
- `FLASK_SECRET_KEY` changed
- Production server configured (gunicorn/nginx)

**Happy coding! 🚀**
