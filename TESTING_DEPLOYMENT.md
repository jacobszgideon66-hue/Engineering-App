# Testing & Deployment Guide

## Local Testing

### 1. Setup Test Environment
```bash
cd /home/gideon/Engineeringapplication/backend
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run All Tests
```bash
pytest test_api.py -v
```

### 3. Run Specific Test Categories

**Authentication Tests**
```bash
pytest test_api.py -k "test_user_" -v
```

**Inventory Tests**
```bash
pytest test_api.py -k "test_list_inventory" -v
```

**API Security Tests**
```bash
pytest test_api.py -k "unauthorized" -v
```

### 4. Generate Test Coverage Report
```bash
pytest --cov=. test_api.py --cov-report=html
open htmlcov/index.html
```

## Manual Testing with cURL

### Test Health Endpoint
```bash
curl -X GET http://localhost:8000/health
```

### Register User
```bash
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123",
    "full_name": "Test User",
    "role": "mechanic"
  }'
```

### Login & Get Token
```bash
curl -X POST http://localhost:8000/users/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass123"
```

### Access Protected Endpoint
```bash
TOKEN="your_token_here"
curl -X GET http://localhost:8000/inventory/ \
  -H "Authorization: Bearer $TOKEN"
```

## Mobile App Testing

### Testing on iOS
1. Use Xcode or simulator
2. Ensure API running on `192.168.x.x:8000` (not localhost)
3. Update API URL in iOS app settings
4. Add security exception if using HTTP

### Testing on Android
1. Use Android Studio emulator or physical device
2. Update API URL to `10.0.2.2:8000` (emulator) or device IP
3. Add HTTPS exception in Android manifest if needed

### Common Issues

**iOS Cannot Connect to API**
- Ensure API is accessible from your network
- Check firewall settings
- Use `ngrok` for tunneling: `ngrok http 8000`

**Android Emulator Connection**
- Use `10.0.2.2` instead of `localhost`
- For physical device: use machine IP address
- Check network connectivity

## Performance Testing

### Load Testing with Apache Bench
```bash
# Install ab
# macOS: brew install httpd
# Ubuntu: apt-get install apache2-utils

# Test endpoint
ab -n 1000 -c 10 http://localhost:8000/health
```

### Load Testing with Locust
```bash
# Install
pip install locust

# Create locustfile.py
# Run: locust -f locustfile.py --host=http://localhost:8000
```

## Database Verification

### Check SQLite Database
```bash
sqlite3 mechanical_app.db
.tables
SELECT * FROM users;
.exit
```

### Check PostgreSQL Database
```bash
psql -U engineeringapp -d mechanical_app -h localhost
\dt  # List tables
SELECT * FROM users;
\q  # Quit
```

## Docker Deployment Testing

### Build Docker Image
```bash
cd /home/gideon/Engineeringapplication
docker build -t engineering-app:latest .
```

### Run Container
```bash
docker run -p 8000:8000 \
  -e SECRET_KEY="test_key" \
  -e DATABASE_URL="sqlite:///./mechanical_app.db" \
  engineering-app:latest
```

### Test Docker Compose Setup
```bash
docker-compose up -d
docker-compose ps  # Check status
docker-compose logs -f backend  # View logs
curl http://localhost:8000/health
docker-compose down
```

## Continuous Integration (CI/CD)

### GitHub Actions Example
Create `.github/workflows/tests.yml`:

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
          python-version: 3.11
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          pytest test_api.py -v
```

## Production Deployment Checklist

- [ ] Update `SECRET_KEY` in production .env
- [ ] Set `DEBUG=False`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Configure ALLOWED_ORIGINS properly
- [ ] Set up HTTPS/SSL certificate
- [ ] Configure reverse proxy (Nginx)
- [ ] Set up database backups
- [ ] Configure logging and monitoring
- [ ] Run final tests
- [ ] Deploy to production server

## Monitoring & Logging

### View Application Logs
```bash
# Local
python -c "import logging; logging.basicConfig(level=logging.DEBUG)"

# Docker
docker-compose logs -f backend --tail=100
```

### Health Check
```bash
curl -X GET http://localhost:8000/health
```

### Database Connectivity Check
```bash
python -c "from database import SessionLocal; db = SessionLocal(); print('DB Connected!')"
```

## Rollback Procedures

### Docker Rollback
```bash
# Stop current version
docker-compose down

# Revert to previous image
docker image ls
docker run -p 8000:8000 engineering-app:previous-tag
```

### Manual Rollback
```bash
cd /home/gideon/Engineeringapplication/backend
git checkout HEAD~1
# Restart application
```

## Performance Optimization

### Database Query Optimization
```sql
-- Add indexes for frequently queried fields
CREATE INDEX idx_user_username ON users(username);
CREATE INDEX idx_inventory_category ON inventory(category);
CREATE INDEX idx_job_card_status ON job_cards(status);
```

### Caching Strategy
- Cache user roles for 1 hour
- Cache inventory items for 30 minutes
- Invalidate cache on updates

### Connection Pooling
Already configured in `database.py`:
- Pool size: 10
- Max overflow: 20
- Pool recycle: 3600 seconds

---

For more information, see the main README.md file.
