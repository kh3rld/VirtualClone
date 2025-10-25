# VirtualClone Setup Guide

Complete guide to setting up and running the VirtualClone application locally and in production.

## Table of Contents
- [System Requirements](#system-requirements)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements
- **OS**: Linux, macOS, or Windows 10+
- **Python**: 3.9+ (recommended: 3.11+)
- **RAM**: 4GB minimum, 8GB+ recommended
- **Disk Space**: 5GB for models and dependencies
- **Internet**: Required for initial model downloads

### Optional Requirements
- **CUDA**: For GPU acceleration (NVIDIA GPU with CUDA 11.8+)
- **FFmpeg**: Required for audio/video processing features
- **Flutter SDK**: For mobile app development (optional)

### System Dependencies

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv ffmpeg git
```

#### macOS
```bash
brew install python3 ffmpeg git
```

#### Windows
1. Install Python 3.11+ from [python.org](https://python.org)
2. Install FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
3. Install Git from [git-scm.com](https://git-scm.com)

## Quick Start

For experienced developers who want to get running quickly:

```bash
# Clone and enter the project
cd VirtualClone

# Create virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run tests
pytest

# Start development server
python run.py
```

The application will be available at http://localhost:5050

## Detailed Setup

### 1. Clone the Repository

```bash
cd VirtualClone
```

### 2. Create Python Virtual Environment

A virtual environment isolates project dependencies:

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
# On Linux/macOS:
source .venv/bin/activate

# On Windows (Command Prompt):
.venv\Scripts\activate.bat

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
```

You should see `(.venv)` in your terminal prompt.

### 3. Upgrade pip and Install Dependencies

```bash
# Upgrade pip, setuptools, and wheel
pip install -U pip setuptools wheel

# Install project dependencies
pip install -r requirements.txt
```

**Note**: Initial installation may take 5-15 minutes depending on your internet connection, as it downloads AI models.

#### Optional: GPU Support

For NVIDIA GPU acceleration (Linux/Windows only):

```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# If False, install PyTorch with CUDA support:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 4. Configure Environment Variables

```bash
# Copy example configuration
cp .env.example .env

# Edit with your preferred editor
nano .env
# or
code .env
```

**Important**: Change `FLASK_SECRET_KEY` in production:

```python
# Generate a secure secret key:
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Create Required Directories

The application will create these automatically, but you can create them manually:

```bash
mkdir -p uploads downloads data
```

### 6. Verify Installation

```bash
# Run tests to verify everything is working
pytest -v

# Expected output: 57 passed
```

## Configuration

### Environment Variables Reference

Edit `.env` to customize the application:

#### Flask Configuration
```bash
# Secret key for sessions (CHANGE IN PRODUCTION!)
FLASK_SECRET_KEY=your-secret-key-here-change-this-in-production

# Environment: development, staging, production
FLASK_ENV=development

# Enable debug mode (NEVER in production)
FLASK_DEBUG=True

# Server binding
FLASK_HOST=0.0.0.0  # 0.0.0.0 = all interfaces, 127.0.0.1 = localhost only
FLASK_PORT=5050
```

#### Upload Configuration
```bash
# Maximum file upload size (bytes)
MAX_CONTENT_LENGTH=31457280  # 30MB

# Upload directories
UPLOAD_FOLDER=uploads
DOWNLOADS_FOLDER=downloads

# Allowed video file extensions
ALLOWED_EXTENSIONS=mp4,mov,avi,mkv

# Maximum number of videos to process
MAX_VIDEOS=5
```

#### AI Model Configuration
```bash
# Translation model (HuggingFace model ID)
AI_MODEL_TRANSLATION=facebook/nllb-200-distilled-600M

# Question-answering model
AI_MODEL_QA=deepset/roberta-base-squad2

# Whisper model size: tiny, base, small, medium, large
WHISPER_MODEL=tiny
```

#### AI Behavior Tuning
```bash
# Number of top answers to consider (primary mode)
AI_QA_TOP_K_PRIMARY=3

# Number of top answers for diverse responses
AI_QA_TOP_K_DIVERSE=5

# Maximum answer length in characters
AI_MAX_ANSWER_LEN=150

# Number of recent conversation exchanges to include as context
CONVERSATION_RECENT_EXCHANGES=3

# Number of recent questions to check for repetition
REPETITION_HISTORY_WINDOW=5

# Similarity threshold for detecting repetitive questions (0.0-1.0)
REPETITION_SIMILARITY_THRESHOLD=0.7
```

#### Session Configuration
```bash
# Session storage type
SESSION_TYPE=filesystem

# Make sessions permanent
SESSION_PERMANENT=False

# Sign session cookies
SESSION_USE_SIGNER=True

# Session lifetime in seconds
PERMANENT_SESSION_LIFETIME=3600
```

#### Logging
```bash
# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# Log file path
LOG_FILE=app.log
```

## Running the Application

### Development Mode

```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows

# Start development server
python run.py
```

Access the application at:
- Web UI: http://localhost:5050
- API: http://localhost:5050/api/v1
- Health check: http://localhost:5050/hello

### Production Mode

#### Option 1: Gunicorn (Linux/macOS)

```bash
# Install gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5050 --timeout 120 'run:app'

# Or with more options:
gunicorn \
  --workers 4 \
  --bind 0.0.0.0:5050 \
  --timeout 120 \
  --access-logfile access.log \
  --error-logfile error.log \
  --log-level info \
  'run:app'
```

#### Option 2: uWSGI

```bash
# Install uwsgi
pip install uwsgi

# Run
uwsgi --http 0.0.0.0:5050 --wsgi-file run.py --callable app --processes 4 --threads 2
```

#### Option 3: Docker

```dockerfile
# Example Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create necessary directories
RUN mkdir -p uploads downloads data

# Expose port
EXPOSE 5050

# Run application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5050", "--timeout", "120", "run:app"]
```

Build and run:
```bash
docker build -t virtualclone .
docker run -p 5050:5050 -v $(pwd)/uploads:/app/uploads virtualclone
```

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_ai_service.py

# Run with coverage
pytest --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Mobile App (Flutter)

If you want to develop the mobile app:

```bash
# Install Flutter SDK (follow official guide)
# https://docs.flutter.dev/get-started/install

# Navigate to flutter app
cd flutter_app

# Get dependencies
flutter pub get

# Run on connected device/emulator
flutter run

# Build for Android
flutter build apk

# Build for iOS (macOS only)
flutter build ios
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem**: `ModuleNotFoundError: No module named 'flask'`

**Solution**:
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### 2. Port Already in Use

**Problem**: `Address already in use`

**Solution**:
```bash
# Find process using port 5050
lsof -i :5050  # Linux/macOS
netstat -ano | findstr :5050  # Windows

# Kill the process or change FLASK_PORT in .env
```

#### 3. Model Download Fails

**Problem**: Models fail to download or timeout

**Solution**:
```bash
# Download models manually
python -c "from transformers import pipeline; pipeline('translation', model='facebook/nllb-200-distilled-600M')"
python -c "from transformers import pipeline; pipeline('question-answering', model='deepset/roberta-base-squad2')"
```

#### 4. FFmpeg Not Found

**Problem**: `FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'`

**Solution**:
```bash
# Install FFmpeg
# Ubuntu/Debian:
sudo apt install ffmpeg

# macOS:
brew install ffmpeg

# Windows: Download from ffmpeg.org and add to PATH
```

#### 5. CUDA Not Available

**Problem**: GPU not being used

**Solution**:
```bash
# Check CUDA availability
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}, Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}')"

# Install CUDA-enabled PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### 6. Tests Fail to Discover

**Problem**: `collected 0 items`

**Solution**:
```bash
# Ensure you're in project root
cd /path/to/VirtualClone

# Run pytest from project root
pytest

# Or specify test directory explicitly
pytest tests/
```

#### 7. Permission Errors

**Problem**: Cannot write to uploads/downloads directories

**Solution**:
```bash
# Create directories with proper permissions
mkdir -p uploads downloads data
chmod 755 uploads downloads data

# On Linux, ensure your user owns the directories
sudo chown -R $USER:$USER uploads downloads data
```

### Getting Help

If you encounter issues not covered here:

1. Check the logs: `tail -f app.log`
2. Run tests with verbose output: `pytest -vv`
3. Check GitHub Issues: 
4. Enable debug mode: Set `FLASK_DEBUG=True` in `.env`

### Performance Optimization

#### For Development
```bash
# Use lighter models for faster loading
WHISPER_MODEL=tiny
AI_MODEL_QA=distilbert-base-cased-distilled-squad
```

#### For Production
```bash
# Use larger models for better accuracy
WHISPER_MODEL=base  # or small
AI_MODEL_QA=deepset/roberta-base-squad2

# Enable GPU if available
# (Automatically detected)

# Increase workers based on CPU cores
gunicorn -w $((2 * $(nproc) + 1)) ...
```

## Next Steps

- See [TESTING_GUIDE.md](TESTING_GUIDE.md) for detailed testing instructions
- See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment guide
- See [MOBILE_DEPLOYMENT.md](MOBILE_DEPLOYMENT.md) for mobile app deployment
- Check [README.md](README.md) for project overview and features
