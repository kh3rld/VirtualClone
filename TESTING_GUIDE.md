# VirtualClone Testing Guide

Complete guide for testing the VirtualClone application.

## Quick Start

```bash
# Install testing dependencies
pip install pytest pytest-flask pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html tests/
```

## Test Structure

### Test Files

```
tests/
├── __init__.py
├── test_config.py              # Configuration tests
├── test_context_loader.py      # Context loading tests
└── test_app.py                 # Flask application tests
```

### Manual Test Scripts

```
test_conversation_context.py    # Test conversation features
test_conversation_demo.py        # End-to-end conversation test
```


## Running Tests

### All Tests
```bash
pytest
```

### Verbose Output
```bash
pytest -v
```

### Specific Test File
```bash
pytest tests/test_config.py -v
```

### Specific Test Function
```bash
pytest tests/test_config.py::TestConfig::test_secret_key_not_empty -v
```

### With Coverage Report
```bash
pytest --cov=app --cov-report=term-missing tests/
```

### Generate HTML Coverage Report
```bash
pytest --cov=app --cov-report=html tests/
# Open htmlcov/index.html in browser
```


## Manual Testing

### 1. Configuration Tests

```bash
python -c "
from app.config import Config
print(f'SECRET_KEY set: {bool(Config.SECRET_KEY)}')
print(f'DEBUG: {Config.DEBUG}')
print(f'Upload folder: {Config.UPLOAD_FOLDER}')
"
```

### 2. Context Loader Tests

```bash
python -c "
from app.services.context_loader import load_context
context = load_context()
print(f'Context loaded: {len(context)} chars')
"
```

### 3. AI Service Tests

```bash
python -c "
from app.services.ai_service import AIService
service = AIService()
print(f'Service created')
print(f'Cache size: {service.response_cache.maxsize}')
"
```

### 4. Flask App Tests

```bash
python -c "
from app import create_app
app = create_app()
print(f'App created')
print(f'Blueprints: {list(app.blueprints.keys())}')
"
```

### 5. Route Tests

```bash
python -c "
from app import create_app
app = create_app()
app.config['TESTING'] = True
with app.test_client() as client:
    response = client.get('/hello')
    print(f'/hello status: {response.status_code}')
    response = client.get('/')
    print(f'/ status: {response.status_code}')
"
```


## Integration Testing

### 1. Full Conversation Test

```bash
python test_conversation_context.py
```

**Expected Output:**
```
Testing Conversation Context Implementation
==================================================
AI Service import successful
AI Service instance created
Context building works
Similarity detection works
Repetitive question detection works
All tests passed!
```

### 2. Conversation Demo

```bash
python test_conversation_demo.py
```

**Note:** This test takes 2-3 minutes due to model loading.


## Performance Testing

### Startup Time Test

```bash
time python -c "from app import create_app; app = create_app(); print('Started')"
```

**Expected:** <5 seconds (lazy loading)

### Memory Usage Test

```bash
python -c "
import tracemalloc
tracemalloc.start()

from app.services.ai_service import AIService
service = AIService(cache_size=10)

# Add items to cache
for i in range(20):
    service.response_cache[f'key{i}'] = f'value{i}'

current, peak = tracemalloc.get_traced_memory()
print(f'Current memory: {current / 10**6:.1f} MB')
print(f'Peak memory: {peak / 10**6:.1f} MB')
print(f'Cache size (should be 10): {len(service.response_cache)}')
tracemalloc.stop()
"
```

---

## Load Testing

### Simple Load Test

```bash
# Install Apache Bench
# Ubuntu/Debian: sudo apt-get install apache2-utils
# MacOS: brew install ab

# Start the server
python run.py &
SERVER_PID=$!

# Wait for server to start
sleep 2

# Run load test (100 requests, 10 concurrent)
ab -n 100 -c 10 http://localhost:5050/hello

# Stop server
kill $SERVER_PID
```


## Continuous Integration

### GitHub Actions Example

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov

    - name: Run tests
      run: |
        pytest --cov=app tests/

    - name: Upload coverage
      uses: codecov/codecov-action@v2
```


## Test Coverage Goals

| Component | Target Coverage | Current |
|-----------|----------------|---------|
| Config | 100% | ✅ 100% |
| Context Loader | 100% | ✅ 100% |
| AI Service | 80% | ✅ ~85% |
| Routes | 80% | ✅ ~75% |
| Controllers | 70% | ⚠️ ~60% |
| **Overall** | **80%** | **~75%** |


## Writing New Tests

### Example: Testing a New Route

```python
# tests/test_new_route.py
import pytest
from app import create_app


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


class TestNewRoute:
    def test_route_exists(self, client):
        response = client.get('/new-route')
        assert response.status_code == 200

    def test_route_returns_json(self, client):
        response = client.get('/new-route')
        assert response.content_type == 'application/json'

    def test_route_with_data(self, client):
        response = client.post('/new-route', json={'key': 'value'})
        assert response.status_code == 200
        data = response.get_json()
        assert 'result' in data
```


## Debugging Tests

### Run with PDB

```bash
pytest --pdb
```

This will drop into debugger on failures.

### Print Debug Output

```bash
pytest -s
```

Shows print statements during tests.

### Verbose Failures

```bash
pytest -vv
```

Shows very detailed output.


## Common Test Failures

### 1. Import Errors

**Problem:** `ModuleNotFoundError: No module named 'app'`

**Solution:**
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

### 2. Context File Not Found

**Problem:** `Context file not found`

**Solution:** Ensure `llm-script.txt` exists in project root, or tests will use empty context.

### 3. Port Already in Use

**Problem:** `Address already in use`

**Solution:**
```bash
# Find and kill process using port 5050
lsof -ti:5050 | xargs kill -9
```

### 4. Model Loading Timeout

**Problem:** Tests timeout during model loading

**Solution:** Skip model loading tests or increase timeout:
```python
@pytest.mark.slow
def test_with_model_loading():
    # Test code here
    pass

# Run without slow tests:
# pytest -m "not slow"
```


## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Use Fixtures**: Share common setup across tests
3. **Mock External Services**: Don't rely on network/external APIs
4. **Test Edge Cases**: Not just happy path
5. **Keep Tests Fast**: Mock slow operations
6. **Clear Test Names**: Describe what is being tested
7. **One Assert Per Test**: Or logically grouped asserts
8. **Clean Up**: Use fixtures for teardown


## Test Checklist

Before committing code:

- [ ] All tests pass locally
- [ ] New features have tests
- [ ] Bug fixes have regression tests
- [ ] Coverage is maintained/improved
- [ ] No warnings or errors
- [ ] Documentation updated
- [ ] Manual smoke test performed


## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Flask Testing](https://flask.palletsprojects.com/en/latest/testing/)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)


