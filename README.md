# 🌍 Landsat Image Viewer

A comprehensive web application for viewing and processing Landsat satellite imagery with real-time notifications and interactive mapping capabilities.

## ✨ Features

### 🔐 Authentication & Security
- **JWT-based authentication** with secure token management
- **Argon2 password hashing** (no bcrypt as requested)
- **Email confirmation workflow** with Mailchimp integration
- **Password strength validation** with OWASP/MIT compliance
- **Secure password reset** functionality

### 🛰️ Landsat Processing Pipeline
- **Background job processing** with Celery + Redis
- **Landsat 8 image downloading** (bands 5, 6, 7, 8: NIR, SWIR-1, SWIR-2, PAN)
- **K-means clustering segmentation** algorithm
- **Real-time job notifications** via Server-Sent Events
- **Image export** in multiple formats (PNG, JPG, TIFF)

### 🗺️ Interactive Mapping
- **Leaflet map integration** with click-to-select regions
- **Location management** with CRUD operations
- **Geographic coordinate validation** and area calculation
- **Responsive design** with mobile-friendly interface

### 🏗️ Production-Ready Infrastructure
- **Docker containerization** for all services
- **Nginx reverse proxy** with SSL support and security headers
- **Supabase integration** for database and file storage
- **Environment-based configuration** management
- **Comprehensive testing** with pytest and coverage reports

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- Supabase account
- Mailchimp account (for email confirmations)
- Landsat API credentials

### 1. Environment Setup

#### For Development
```bash
# Copy development environment configuration
cp dev.env .env

# Edit .env with your credentials (for development, placeholders are fine)
nano .env
```

#### For Production
```bash
# Copy production environment configuration
cp prod.env .env

# Edit .env with your actual credentials
nano .env
```

**Development Environment (dev.env):**
- Uses SQLite database (no external setup needed)
- Contains placeholder values for external services
- Debug mode enabled

**Production Environment (prod.env):**
- Requires real Supabase, Mailchimp, and Landsat API credentials
- Debug mode disabled
- Security-hardened settings

**Required Environment Variables for Production:**
```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
SUPABASE_STORAGE_BUCKET=landsat-images

# Email Service (Mailchimp)
MAILCHIMP_API_KEY=your-mailchimp-api-key
MAILCHIMP_FROM_EMAIL=noreply@yourdomain.com

# Landsat API
LANDSAT_API_USERNAME=your-landsat-username
LANDSAT_API_PASSWORD=your-landsat-password

# Security
SECRET_KEY=your-super-secret-key-minimum-32-characters
```

### 2. Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run with Docker (recommended)
docker-compose up -d

# Or run manually
# Start Redis: redis-server
# Start Celery: celery -A app.core.celery_app worker --loglevel=info
# Start FastAPI: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend Setup

```bash
cd frontend

# Install Node.js dependencies
npm install

# Start development server
npm start
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Nginx (Docker)**: http://localhost:80

## 🧪 Testing

### Run All Tests
```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
python run_tests.py

# Run with coverage
python run_tests.py --coverage
```

### Test Categories
```bash
# Unit tests only
python run_tests.py --unit

# Integration tests only
python run_tests.py --integration

# Authentication tests only
python run_tests.py --auth

# Location tests only
python run_tests.py --location
```

## 🏗️ Architecture

### Backend Structure
```
app/
├── api/v1/                 # API endpoints
│   ├── auth.py            # Authentication routes
│   ├── locations.py       # Location management
│   └── events.py          # Real-time notifications
├── core/                  # Core functionality
│   ├── config.py         # Configuration management
│   ├── database.py       # Database connection
│   ├── security.py       # Security utilities
│   └── celery_app.py     # Background job configuration
├── models/               # Database models
│   ├── base.py          # Base model with UUIDv7
│   ├── user.py          # User model
│   └── location.py      # Location model
├── schemas/             # Pydantic schemas
│   ├── auth.py          # Authentication schemas
│   └── location.py      # Location schemas
├── services/           # Business logic
│   ├── auth_service.py    # Authentication service
│   ├── location_service.py # Location service
│   └── storage_service.py  # Supabase storage
└── tasks/             # Celery tasks
    ├── landsat_tasks.py   # Image downloading
    └── image_processing.py # Image segmentation
```

### Frontend Structure
```
frontend/src/
├── components/         # Reusable components
│   ├── ImageViewer.tsx    # Image viewing with zoom
│   ├── LocationForm.tsx   # Location creation form
│   ├── LocationList.tsx   # Location listing
│   ├── NotificationCenter.tsx # Real-time notifications
│   └── MapInteractionHandler.tsx # Map click handling
├── pages/             # Page components
│   ├── LoginPage.tsx     # Authentication
│   ├── RegisterPage.tsx  # User registration
│   └── DashboardPage.tsx # Main dashboard
├── hooks/            # Custom React hooks
│   └── useNotifications.ts # SSE notification hook
├── store/           # State management
│   ├── authStore.ts     # Authentication state
│   └── locationStore.ts # Location state
└── types/          # TypeScript definitions
    ├── auth.ts        # Authentication types
    └── location.ts    # Location types
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SUPABASE_URL` | Supabase project URL | ✅ |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key | ✅ |
| `MAILCHIMP_API_KEY` | Mailchimp transactional API key | ✅ |
| `LANDSAT_API_USERNAME` | Landsat API username | ✅ |
| `LANDSAT_API_PASSWORD` | Landsat API password | ✅ |
| `SECRET_KEY` | JWT secret key (min 32 chars) | ✅ |
| `DEBUG` | Enable debug mode | ❌ |

### Docker Services

- **fastapi**: Main application container
- **celery-worker**: Background job processing
- **redis**: Message broker and cache
- **nginx**: Reverse proxy and load balancer
- **supabase**: Database (external service)

## 🔒 Security Features

- **Argon2 password hashing** (industry standard)
- **JWT token authentication** with refresh tokens
- **CORS protection** with configurable origins
- **Rate limiting** on API endpoints
- **Input validation** and sanitization
- **SQL injection protection**
- **XSS protection** headers
- **Secure file upload** handling

## 📊 Monitoring

### Health Checks
- **Application Health**: `GET /health`
- **Database Connectivity**: Automatic health monitoring
- **Celery Workers**: Background job status

### Logging
- **Structured logging** with configurable levels
- **Error tracking** and reporting
- **Performance monitoring** metrics

### Real-time Monitoring
- **Server-Sent Events** for live updates
- **Background job progress** tracking
- **User activity** monitoring

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**
```bash
# Set production environment variables
export NODE_ENV=production
export DEBUG=false
```

2. **Docker Deployment**
```bash
# Build and deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Or use Docker Swarm
docker stack deploy -c docker-compose.prod.yml landsat-viewer
```

3. **SSL Configuration**
```bash
# Update nginx configuration with SSL certificates
# Place certificates in nginx/ssl/ directory
# Update SUPABASE_URL to production instance
```

### Scaling

- **Horizontal scaling** with multiple worker instances
- **Load balancing** via Nginx upstream configuration
- **Database connection pooling** for high availability

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

### Development Guidelines

- **Code Style**: Follow PEP 8 for Python, ESLint for TypeScript
- **Testing**: Write tests for all new features
- **Documentation**: Update README for significant changes
- **Security**: Follow OWASP guidelines

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Landsat Program** - USGS/NASA satellite imagery
- **Supabase** - Backend-as-a-Service platform
- **Leaflet** - Interactive mapping library
- **FastAPI** - Modern web framework
- **React** - User interface library

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the test suite for examples

---

**Built with ❤️ for satellite imagery analysis and research**
