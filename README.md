# Engineering & Mining Application

A comprehensive mobile-first asset management system for mechanical engineering and mining operations. Built with FastAPI backend, with full iOS and Android compatibility.

## 🚀 Features

- ✅ **User Management** - Role-based access control (mechanic, manager, admin)
- ✅ **Inventory Management** - Track parts, tools, and consumables in real-time
- ✅ **Job Card System** - Create, manage, and track work orders
- ✅ **Quotations & Invoices** - Generate and manage customer quotes and invoices
- ✅ **Safety Documentation** - Document and digitally sign safety reports
- ✅ **Mobile-First Design** - Fully responsive and compatible with iOS & Android
- ✅ **CORS Enabled** - Ready for mobile app integration
- ✅ **JWT Authentication** - Secure token-based authentication
- ✅ **File Uploads** - Support for job card images and reports

## 📋 System Architecture

```
Engineering Application/
├── backend/              # FastAPI Python backend
│   ├── Routes/          # API route handlers
│   ├── models.py        # Database models (SQLAlchemy)
│   ├── schemas.py       # Pydantic validation schemas
│   ├── auth.py          # JWT authentication logic
│   ├── database.py      # Database connection & pooling
│   ├── main.py          # FastAPI application setup
│   ├── static/          # Frontend HTML/CSS/JS
│   ├── uploads/         # File upload directory
│   ├── requirements.txt  # Python dependencies
│   └── .env             # Environment configuration
├── Frontend/            # Mobile app frontend (React/Vue)
├── Dockerfile          # Container image definition
└── docker-compose.yml  # Multi-container orchestration
```

## 🔧 Installation & Setup

### Prerequisites
- Python 3.9+
- pip or poetry
- Docker & Docker Compose (optional)
- Git

### Local Development Setup

1. **Clone and Navigate**
```bash
cd /home/gideon/Engineeringapplication
```

2. **Create Virtual Environment**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run the Application**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

6. **Access the Application**
- Web UI: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

1. **Build and Start Services**
```bash
docker-compose up -d
```

2. **Initialize Database (first run)**
```bash
docker-compose exec backend python -c "from database import engine; import models; models.Base.metadata.create_all(bind=engine)"
```

3. **Check Service Status**
```bash
docker-compose ps
```

4. **View Logs**
```bash
docker-compose logs -f backend
```

5. **Stop Services**
```bash
docker-compose down
```

## 📱 Mobile App Integration

### iOS & Android Compatibility

The API is fully compatible with iOS and Android applications through:

1. **CORS Headers** - All endpoints return proper CORS headers
2. **JSON API** - Standard RESTful JSON responses
3. **JWT Authentication** - Secure token-based auth
4. **File Uploads** - Multipart form data support
5. **Error Handling** - Standard HTTP status codes

### Example Mobile Request (Flutter/React Native)

```dart
// Dart/Flutter Example
final client = http.Client();
final token = 'YOUR_ACCESS_TOKEN';

final response = await client.get(
  Uri.parse('http://your-api.com/inventory/'),
  headers: {
    'Authorization': 'Bearer $token',
    'Content-Type': 'application/json',
  },
);

final inventory = jsonDecode(response.body);
```

## 🧪 Testing

### Run Tests
```bash
cd backend
pytest test_api.py -v
```

### Run Specific Test
```bash
pytest test_api.py::test_user_login -v
```

### Generate Coverage Report
```bash
pytest --cov=. test_api.py
```

## 📚 API Documentation

### Authentication
```bash
# Register User
POST /users/register
{
  "username": "mechanic1",
  "password": "secure_password",
  "full_name": "John Mechanic",
  "role": "mechanic"  # mechanic, manager, admin
}

# Login
POST /users/token
{
  "username": "mechanic1",
  "password": "secure_password"
}
```

### Inventory
```bash
# List Inventory
GET /inventory/
Header: Authorization: Bearer {token}

# Create Item (Manager/Admin only)
POST /inventory/
{
  "part_number": "PART123",
  "name": "Hydraulic Pump",
  "category": "Part",
  "stock_level": 5,
  "price": 250.00
}

# Search by Category
GET /inventory/search/by-category?category=Tool

# Get Low Stock Items
GET /inventory/search/low-stock?threshold=10
```

### Job Cards
```bash
# Create Job Card
POST /job-cards/
{
  "mechanic_id": 1,
  "machine_id": 1,
  "problem_description": "Machine not starting"
}

# Upload Report Image
POST /job-cards/{card_id}/upload-report
[multipart/form-data]
file: <image_file>

# Update Status
PUT /job-cards/{card_id}
{
  "status": "in-progress",
  "work_performed": "Replaced oil filter"
}
```

### Quotations
```bash
# Create Quotation
POST /quotations/
{
  "customer_name": "ABC Company",
  "total_amount": 5000.00
}

# Update Status
PUT /quotations/{id}/status
{
  "status": "approved"  # draft, sent, approved, rejected, invoiced
}
```

### Invoices
```bash
# Create Invoice from Quotation
POST /invoices/
{
  "quotation_id": 1
}

# Update Invoice Status
PUT /invoices/{id}/status
{
  "status": "paid"  # issued, paid, overdue, cancelled
}
```

### Safety Documents
```bash
# Create Safety Document
POST /safety-docs/
{
  "job_card_id": 1,
  "title": "Site Safety Report"
}

# Sign Document
POST /safety-docs/{doc_id}/sign
{
  "signature_data": "base64_encoded_signature_image"
}
```

## 🔐 Security Best Practices

1. **Environment Variables**
   - Always use `.env` for secrets
   - Never commit `.env` to version control
   - Use strong `SECRET_KEY` in production

2. **CORS Configuration**
   - Restrict `allow_origins` to specific domains in production
   - Current: `allow_origins=["*"]` (development only)

3. **SSL/TLS**
   - Always use HTTPS in production
   - Use reverse proxy (Nginx) or load balancer

4. **Rate Limiting**
   - Implement rate limiting for production
   - Consider using Redis for distributed rate limiting

5. **Database**
   - Use PostgreSQL instead of SQLite in production
   - Implement regular backups
   - Use connection pooling

## 🚀 Production Deployment

### Using Nginx & Gunicorn

1. **Install Gunicorn**
```bash
pip install gunicorn
```

2. **Run with Gunicorn**
```bash
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

3. **Configure Nginx** (reverse proxy)
```nginx
upstream api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/backend/static;
    }
}
```

### Using Cloud Platforms

**Heroku:**
```bash
git push heroku main
```

**AWS (using Elastic Beanstalk):**
```bash
eb create
eb deploy
```

**Google Cloud (using Cloud Run):**
```bash
gcloud run deploy
```

## 📈 Performance Optimization

1. **Database Indexing**
   - Add indexes to frequently queried fields
   - Monitor slow queries

2. **Caching**
   - Implement Redis caching for inventory
   - Cache user roles and permissions

3. **API Pagination**
   - All list endpoints support `skip` and `limit` parameters
   - Default limit: 100 items

4. **Async Operations**
   - All endpoints use async/await
   - Supports concurrent requests

## 🐛 Troubleshooting

### Connection Issues
```bash
# Check if API is running
curl http://localhost:8000/health

# Check logs
docker-compose logs backend
```

### Database Issues
```bash
# Reset database (development only)
rm mechanical_app.db

# Restart container
docker-compose restart backend
```

### CORS Issues
```bash
# Verify CORS headers
curl -H "Origin: http://localhost:3000" http://localhost:8000/inventory/
```

## 📞 Support & Documentation

- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **GitHub Issues**: [Report bugs]
- **Email**: support@yourdomain.com

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🙋 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 🎯 Roadmap

- [ ] Mobile React Native app
- [ ] Flutter mobile app
- [ ] Analytics dashboard
- [ ] Advanced reporting
- [ ] Machine learning predictions
- [ ] Real-time notifications
- [ ] Offline mode support
- [ ] Multi-language support

---

**Built with ❤️ for Engineering Professionals**
