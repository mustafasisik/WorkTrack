# WorkTrack

WorkTrack is a sophisticated employee tracking and management system built with Django, designed to streamline workforce management through separate interfaces for staff and executives.

## 🚀 Features

- Staff and Executive separate dashboards
- Real-time employee tracking
- Automated task management
- Company information management
- Secure authentication system
- RESTful API integration
- Automated test data generation

## 🛠 Technologies

- **Backend Framework:** Django
- **Task Queue:** Celery
- **Database:** PostgreSQL
- **Containerization:** Docker & Docker Compose
- **Frontend:** HTML, CSS, JavaScript
- **Authentication:** Django Authentication System
- **API:** Django REST Framework

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.x (for local development)
- PostgreSQL (for local development)

## 🔧 Setup and Installation

### Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/WorkTrack.git
   cd WorkTrack
   ```

2. Build and run the containers:
   ```bash
   docker-compose up --build
   ```

3. The application will be available at:
   - Staff Dashboard: http://localhost:8000/staff/
   - Executive Dashboard: http://localhost:8000/executive/

### Local Development Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Update the variables as needed

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Create test data (optional):
   ```bash
   python manage.py create_test_staff
   python manage.py create_company_information
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

7. Start Celery worker:
   ```bash
   celery -A worktrack worker -l info
   ```

## 📁 Project Structure

```
worktrack/
├── core/                   # Main application
│   ├── management/        # Custom management commands
│   ├── templates/         # HTML templates
│   ├── models.py          # Database models
│   ├── views.py           # View controllers
│   ├── urls.py           # URL routing
│   └── tasks.py          # Celery tasks
├── worktrack/             # Project configuration
└── docker-compose.yml     # Docker composition
```

## 🔐 Security

- Secure authentication system
- Role-based access control
- Environment variable management
- Protected API endpoints

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- Your Name - *Initial work*

## 🙏 Acknowledgments

- Django Documentation
- Docker Documentation
- Celery Documentation
