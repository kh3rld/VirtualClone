# Production Deployment Guide

Complete guide for deploying VirtualClone to production environments.

## Table of Contents
- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Environment Setup](#environment-setup)
- [Deployment Options](#deployment-options)
- [Security Best Practices](#security-best-practices)
- [Monitoring & Logging](#monitoring--logging)
- [Backup & Recovery](#backup--recovery)
- [Scaling](#scaling)

## Pre-Deployment Checklist

Before deploying to production, ensure:

- [ ] All tests pass: `pytest`
- [ ] Environment variables configured in `.env`
- [ ] `FLASK_SECRET_KEY` is changed from default
- [ ] `FLASK_DEBUG=False` in production
- [ ] Database backups configured (if using database)
- [ ] SSL/TLS certificates obtained
- [ ] Domain name configured
- [ ] Monitoring tools set up
- [ ] Log rotation configured
- [ ] Firewall rules configured
- [ ] Dependencies security-scanned

## Environment Setup

### Production Environment Variables

Create a production `.env` file:

```bash
# Flask Configuration
FLASK_SECRET_KEY=<generate-with-secrets.token_hex(32)>
FLASK_ENV=production
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5050

# Security
SESSION_USE_SIGNER=True
SESSION_PERMANENT=False

# File Upload (adjust based on your needs)
MAX_CONTENT_LENGTH=52428800  # 50MB
UPLOAD_FOLDER=/var/www/virtualclone/uploads
DOWNLOADS_FOLDER=/var/www/virtualclone/downloads

# AI Models (optimize for production)
AI_MODEL_TRANSLATION=facebook/nllb-200-distilled-600M
AI_MODEL_QA=deepset/roberta-base-squad2
WHISPER_MODEL=base

# Logging
LOG_LEVEL=WARNING
LOG_FILE=/var/log/virtualclone/app.log
```

### Generate Secure Secret Key

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## Deployment Options

### Option 1: Traditional Server (Ubuntu/Debian)

#### 1. Prepare Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv nginx supervisor ffmpeg git

# Create application user
sudo useradd -m -s /bin/bash virtualclone
sudo su - virtualclone
```

#### 2. Deploy Application

```bash
# Clone repository
cd /home/virtualclone
git clone https://github.com/kh3rld/VirtualClone.git app
cd app

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt gunicorn

# Create production .env
cp .env.example .env
nano .env  # Edit with production values

# Create necessary directories
sudo mkdir -p /var/www/virtualclone/{uploads,downloads}
sudo chown -R virtualclone:virtualclone /var/www/virtualclone
sudo mkdir -p /var/log/virtualclone
sudo chown -R virtualclone:virtualclone /var/log/virtualclone
```

#### 3. Configure Supervisor

Create `/etc/supervisor/conf.d/virtualclone.conf`:

```ini
[program:virtualclone]
directory=/home/virtualclone/app
command=/home/virtualclone/app/.venv/bin/gunicorn -w 4 -b 127.0.0.1:5050 --timeout 120 --access-logfile /var/log/virtualclone/access.log --error-logfile /var/log/virtualclone/error.log run:app
user=virtualclone
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/virtualclone/supervisor_err.log
stdout_logfile=/var/log/virtualclone/supervisor_out.log
environment=PATH="/home/virtualclone/app/.venv/bin"
```

Start the service:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start virtualclone
sudo supervisorctl status virtualclone
```

#### 4. Configure Nginx

Create `/etc/nginx/sites-available/virtualclone`:

```nginx
upstream virtualclone {
    server 127.0.0.1:5050 fail_timeout=0;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # File upload size
    client_max_body_size 50M;

    # Timeouts
    proxy_connect_timeout 120;
    proxy_send_timeout 120;
    proxy_read_timeout 120;

    # Static files
    location /static/ {
        alias /home/virtualclone/app/app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Application
    location / {
        proxy_pass http://virtualclone;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://virtualclone/hello;
        access_log off;
    }
}
```

Enable site and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/virtualclone /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 5. SSL with Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal is configured by default
# Test renewal:
sudo certbot renew --dry-run
```

### Option 2: Docker Deployment

#### 1. Create Dockerfile

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads downloads data logs

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5050

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5050/hello')"

# Run application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5050", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "run:app"]
```

#### 2. Create docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    container_name: virtualclone
    restart: unless-stopped
    ports:
      - "5050:5050"
    env_file:
      - .env
    volumes:
      - ./uploads:/app/uploads
      - ./downloads:/app/downloads
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - FLASK_ENV=production
      - FLASK_DEBUG=False
    networks:
      - virtualclone_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5050/hello"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    container_name: virtualclone_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - app
    networks:
      - virtualclone_network

networks:
  virtualclone_network:
    driver: bridge
```

#### 3. Deploy with Docker

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Update deployment
git pull
docker-compose build
docker-compose up -d
```

### Option 3: Cloud Platforms

#### AWS (EC2 + ELB)

```bash
# 1. Launch EC2 instance (Ubuntu 22.04 LTS)
# 2. Configure security groups (allow 80, 443)
# 3. SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# 4. Follow "Traditional Server" deployment steps
# 5. Configure Application Load Balancer (ALB)
# 6. Point domain to ALB DNS
```

#### Google Cloud Platform (GCP)

```bash
# Using Cloud Run (serverless)
gcloud run deploy virtualclone \
  --image gcr.io/PROJECT_ID/virtualclone \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 120s \
  --max-instances 10
```

#### Heroku

```bash
# Install Heroku CLI
# Login
heroku login

# Create app
heroku create virtualclone-prod

# Add buildpacks
heroku buildpacks:add --index 1 https://github.com/heroku/heroku-buildpack-apt
heroku buildpacks:add --index 2 heroku/python

# Create Aptfile for ffmpeg
echo "ffmpeg" > Aptfile

# Set environment variables
heroku config:set FLASK_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
heroku config:set FLASK_ENV=production
heroku config:set FLASK_DEBUG=False

# Deploy
git push heroku main

# Scale
heroku ps:scale web=2
```

#### DigitalOcean App Platform

```yaml
# app.yaml
name: virtualclone
services:
  - name: web
    github:
      repo: kh3rld/VirtualClone
      branch: main
      deploy_on_push: true
    build_command: pip install -r requirements.txt
    run_command: gunicorn -w 4 -b 0.0.0.0:8080 --timeout 120 run:app
    environment_slug: python
    instance_count: 2
    instance_size_slug: professional-xs
    http_port: 8080
    envs:
      - key: FLASK_ENV
        value: production
      - key: FLASK_DEBUG
        value: "False"
      - key: FLASK_SECRET_KEY
        value: YOUR_SECRET_KEY_HERE
        type: SECRET
```

## Security Best Practices

### 1. Environment Variables

Never commit `.env` to version control:
```bash
# .gitignore
.env
*.pyc
__pycache__/
.venv/
uploads/
downloads/
*.log
```

### 2. Secure Headers

Already configured in Nginx example above. If using Flask directly:

```python
# In app/__init__.py
from flask_talisman import Talisman

def create_app():
    app = Flask(__name__)
    
    # Force HTTPS in production
    if not app.config['DEBUG']:
        Talisman(app, 
                 force_https=True,
                 strict_transport_security=True,
                 content_security_policy={
                     'default-src': "'self'",
                     'script-src': ["'self'", "'unsafe-inline'"],
                     'style-src': ["'self'", "'unsafe-inline'"],
                 })
    return app
```

### 3. Rate Limiting

```python
# Install: pip install flask-limiter
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route("/api/v1/chat")
@limiter.limit("10 per minute")
def chat():
    pass
```

### 4. Input Validation

All file uploads are validated. Ensure:
- File size limits enforced
- File type validation
- Filename sanitization

### 5. Secrets Management

Use a secrets manager in production:

```bash
# AWS Secrets Manager
aws secretsmanager create-secret --name virtualclone/flask-secret --secret-string "YOUR_SECRET_KEY"

# In application
import boto3
client = boto3.client('secretsmanager')
response = client.get_secret_value(SecretId='virtualclone/flask-secret')
SECRET_KEY = response['SecretString']
```

## Monitoring & Logging

### Application Monitoring

#### Prometheus + Grafana

```python
# Install: pip install prometheus-flask-exporter
from prometheus_flask_exporter import PrometheusMetrics

app = create_app()
metrics = PrometheusMetrics(app)

# Metrics available at /metrics
```

#### Sentry Error Tracking

```python
# Install: pip install sentry-sdk[flask]
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0,
    environment="production"
)
```

### Log Management

#### Centralized Logging (ELK Stack)

```python
# Install: pip install python-logstash
import logstash

logger.addHandler(logstash.TCPLogstashHandler('logstash-host', 5959))
```

#### Log Rotation

```bash
# /etc/logrotate.d/virtualclone
/var/log/virtualclone/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 virtualclone virtualclone
    sharedscripts
    postrotate
        supervisorctl restart virtualclone
    endscript
}
```

### Health Checks

Implement detailed health endpoint:

```python
@app.route('/health')
def health():
    checks = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'checks': {
            'database': check_database(),
            'disk_space': check_disk_space(),
            'memory': check_memory(),
        }
    }
    status_code = 200 if all(checks['checks'].values()) else 503
    return jsonify(checks), status_code
```

## Backup & Recovery

### 1. Database Backups

If using a database:
```bash
# Automated daily backups
0 2 * * * /usr/bin/pg_dump virtualclone > /backups/db-$(date +\%Y\%m\%d).sql
```

### 2. File Backups

```bash
# Backup uploads and downloads
rsync -avz /var/www/virtualclone/ user@backup-server:/backups/virtualclone/
```

### 3. Configuration Backups

```bash
# Backup environment and configs
tar -czf config-backup-$(date +%Y%m%d).tar.gz .env nginx.conf supervisor.conf
```

### 4. Disaster Recovery Plan

1. Store backups in multiple locations (local + cloud)
2. Test restore procedures regularly
3. Document recovery steps
4. Keep infrastructure as code (Terraform, Ansible)

## Scaling

### Horizontal Scaling

#### Load Balancer Configuration

```nginx
# Nginx load balancer
upstream virtualclone_cluster {
    least_conn;
    server 10.0.1.10:5050 max_fails=3 fail_timeout=30s;
    server 10.0.1.11:5050 max_fails=3 fail_timeout=30s;
    server 10.0.1.12:5050 max_fails=3 fail_timeout=30s;
}
```

#### Session Persistence

Use Redis for shared sessions:

```python
# Install: pip install redis flask-session
from flask_session import Session
import redis

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')
Session(app)
```

### Vertical Scaling

Adjust worker count based on CPU cores:

```bash
# Gunicorn: 2-4 x CPU cores
gunicorn -w $((2 * $(nproc))) ...
```

### Caching

Implement Redis caching for AI responses:

```python
# Install: pip install redis
import redis
import json

cache = redis.Redis(host='localhost', port=6379, decode_responses=True)

def cached_answer(question, context):
    cache_key = f"answer:{hashlib.md5(question.encode()).hexdigest()}"
    cached = cache.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    answer = ai_service.answer_question(question, context)
    cache.setex(cache_key, 3600, json.dumps(answer))
    return answer
```

## Maintenance

### Zero-Downtime Deployments

```bash
# Using supervisor with graceful reload
sudo supervisorctl restart virtualclone

# Or rolling update with multiple workers
# Update code
git pull
# Restart workers one by one
for i in {1..4}; do
    sudo supervisorctl restart virtualclone:virtualclone_$i
    sleep 10
done
```

### Monitoring Checklist

- [ ] CPU usage < 80%
- [ ] Memory usage < 80%
- [ ] Disk usage < 80%
- [ ] Response time < 2s (p95)
- [ ] Error rate < 1%
- [ ] SSL certificate valid (> 30 days)
- [ ] Backups completing successfully
- [ ] Log rotation working

### Update Strategy

1. Test updates in staging environment
2. Schedule maintenance window
3. Notify users
4. Create backup
5. Deploy update
6. Monitor for errors
7. Rollback if necessary

## Support

For deployment issues:
- Check logs: `tail -f /var/log/virtualclone/error.log`
- Check application logs: `tail -f app.log`
- Check Nginx logs: `tail -f /var/log/nginx/error.log`
- Check supervisor: `sudo supervisorctl status`
- Monitor resources: `htop`, `df -h`, `free -h`

## Appendix: Production Checklist

```
Deployment Phase:
[ ] Server provisioned and secured
[ ] Dependencies installed
[ ] Application deployed
[ ] Environment variables configured
[ ] SSL certificates installed
[ ] Nginx/reverse proxy configured
[ ] Firewall configured
[ ] Monitoring set up
[ ] Logging configured
[ ] Backups automated

Security Phase:
[ ] Secret key changed
[ ] Debug mode disabled
[ ] HTTPS enforced
[ ] Security headers configured
[ ] Rate limiting enabled
[ ] Input validation implemented
[ ] File upload restrictions enforced

Testing Phase:
[ ] Health check endpoint responding
[ ] SSL certificate valid
[ ] All routes accessible
[ ] File uploads working
[ ] AI models loading correctly
[ ] Logs being written
[ ] Backups running

Monitoring Phase:
[ ] Uptime monitoring active
[ ] Error tracking configured
[ ] Performance metrics collected
[ ] Alerts configured
[ ] Log aggregation working

Documentation Phase:
[ ] Deployment documented
[ ] Rollback procedure documented
[ ] Troubleshooting guide created
[ ] Team trained
```
