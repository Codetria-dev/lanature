# LaNature - Pet Care Management SaaS

> **A comprehensive SaaS platform for managing your pets' daily care routines, medications, and health tracking.**

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Why LaNature Exists](#why-lanature-exists)
- [Main Features](#main-features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Screenshots](#screenshots)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [What's Out of Scope](#whats-intentionally-out-of-scope)
- [Future Evolutions](#next-possible-evolutions)

---

## Problem Statement

Pet owners face significant challenges in maintaining consistent care routines for their pets:

- **Forgetting critical care tasks**: Missing medication doses, feeding times, or grooming schedules can have serious health consequences
- **Lack of organization**: Managing multiple pets with different needs becomes overwhelming without proper tracking
- **No historical record**: Difficulty tracking what care was provided and when, making it hard to identify patterns or issues
- **Fragmented solutions**: Existing solutions are either too complex, too expensive, or lack essential features
- **Multi-pet management**: Owners with multiple pets struggle to coordinate different routines and schedules

**The result**: Pets receive inconsistent care, health issues go unnoticed, and owners experience stress and guilt from missed care tasks.

---

## Why LaNature Exists

LaNature was created to solve these pain points by providing:

- **Simple, intuitive interface** - No learning curve, just effective pet care management  
- **Automated routine tracking** - Never forget a feeding, medication, or care task again  
- **Complete care history** - Track everything that's been done and identify patterns  
- **Multi-pet support** - Manage all your pets in one unified platform  
- **Affordable solution** - Professional-grade features without enterprise pricing  
- **Privacy-focused** - Your pet data stays secure and private  

**Our mission**: Empower pet owners to provide the best possible care through better organization and consistency.

---

## Main Features

### **Dashboard**
- Overview of all registered pets
- Upcoming care tasks for the day
- Quick access to most-used features
- Visual indicators for pending tasks

### **Pet Management**
- Register multiple pets with detailed profiles
- Track species, breed, birth date, weight, and notes
- Organize pets by household or family
- Edit and update pet information as needed

### **Routine Management**
- Create custom care routines for each pet
- Set up feeding schedules, medication times, and other care tasks
- Configure frequency (daily, weekly, custom)
- Enable/disable routines as needed
- One routine container per pet with multiple tasks

### **Care History**
- Complete log of all care activities
- Filter by pet, task type, or date range
- Track completion status (done, skipped)
- Identify patterns and missed care instances

### **User Authentication**
- Secure registration and login
- JWT-based authentication
- User profile management
- Password protection

### **Admin Panel**
- User management (activate/deactivate users)
- System statistics and analytics
- Administrative settings configuration
- Monitor platform usage and health

### **Internationalization**
- English and Portuguese language support
- Easy to extend to additional languages

---

## Tech Stack

### **Backend**
- **Python 3.11+** - Modern Python with type hints
- **FastAPI** - High-performance, modern web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **PostgreSQL** - Production database (SQLite for development)
- **JWT** - Secure token-based authentication
- **Pydantic** - Data validation using Python type annotations
- **Bcrypt** - Password hashing

### **Frontend**
- **React 18** - Modern UI library
- **Vite** - Next-generation frontend tooling
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client
- **React Router** - Client-side routing
- **i18next** - Internationalization framework

### **DevOps & Tools**
- **Git** - Version control
- **Docker** - Containerization (ready for deployment)
- **Environment Variables** - Configuration management

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  React   │  │  Vite    │  │ Tailwind │  │   Axios   │   │
│  │   18     │  │  Build   │  │    CSS   │  │  Client   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└────────────────────────┬──────────────────────────────────────┘
                         │ HTTP/REST API
                         │ JWT Authentication
┌────────────────────────▼──────────────────────────────────────┐
│                      Backend API                               │
│  ┌────────────────────────────────────────────────────────┐   │
│  │              FastAPI Application                       │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │   │
│  │  │   Auth   │  │  Pets    │  │ Routines │  ...      │   │
│  │  │  Router  │  │  Router  │  │  Router  │           │   │
│  │  └──────────┘  └──────────┘  └──────────┘           │   │
│  └────────────────────────────────────────────────────────┘   │
│  ┌────────────────────────────────────────────────────────┐   │
│  │              Domain Services Layer                      │   │
│  │  ┌──────────────┐  ┌──────────────────┐               │   │
│  │  │ PetService   │  │ ReminderService  │               │   │
│  │  └──────────────┘  └──────────────────┘               │   │
│  └────────────────────────────────────────────────────────┘   │
│  ┌────────────────────────────────────────────────────────┐   │
│  │              Data Access Layer                          │   │
│  │  ┌──────────────┐  ┌──────────────────┐               │   │
│  │  │ SQLAlchemy   │  │   Database       │               │   │
│  │  │    ORM       │  │   Models         │               │   │
│  │  └──────────────┘  └──────────────────┘               │   │
│  └────────────────────────────────────────────────────────┘   │
└────────────────────────┬──────────────────────────────────────┘
                         │
┌────────────────────────▼──────────────────────────────────────┐
│                    Database Layer                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  PostgreSQL (Production) / SQLite (Development)         │  │
│  │                                                          │  │
│  │  • users          • pets          • routines            │  │
│  │  • routine_tasks  • routine_logs  • reminders           │  │
│  │  • reminder_logs  • settings                            │  │
│  └────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

### **Key Architectural Decisions**

- **RESTful API Design**: Clean separation between frontend and backend
- **Service Layer Pattern**: Business logic separated from routing logic
- **JWT Authentication**: Stateless authentication for scalability
- **Database Agnostic**: Supports both PostgreSQL and SQLite
- **Modular Structure**: Easy to extend and maintain

---

## Screenshots

> **Note**: Add screenshots of your application here. Suggested screenshots:
> - Landing page
> - Dashboard view
> - Pet management interface
> - Routine creation form
> - Care history timeline
> - Admin panel

**Example structure:**
```
![Landing Page](docs/screenshots/landing.png)
![Dashboard](docs/screenshots/dashboard.png)
![Pet Management](docs/screenshots/pets.png)
![Routines](docs/screenshots/routines.png)
![History](docs/screenshots/history.png)
![Admin Panel](docs/screenshots/admin.png)
```

---

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Node.js 18+ and npm
- PostgreSQL 12+ (or SQLite for development)
- Git

### Backend Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/lanature.git
cd lanature/backend
```

2. **Create virtual environment**
```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings
DATABASE_URL=postgresql://user:password@localhost:5432/lanature_db
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

5. **Create database**
```sql
CREATE DATABASE lanature_db;
```

6. **Run migrations** (if needed)
```bash
python migrate_db.py
```

7. **Create admin user**
```bash
python create_admin.py
```

8. **Start server**
```bash
uvicorn app.main:app --reload
```

Backend will be available at `http://localhost:8000`  
API docs at `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd ../frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Start development server**
```bash
npm run dev
```

Frontend will be available at `http://localhost:5173`

### Quick Start (Windows)

For Windows users, use the automated setup script:

```powershell
cd backend
.\SETUP-WINDOWS.ps1
```

---

## API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | User login |
| GET | `/api/v1/auth/me` | Get current user info |
| PUT | `/api/v1/auth/me` | Update current user |

### Pet Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/pets/` | List user's pets |
| POST | `/api/v1/pets/` | Create new pet |
| GET | `/api/v1/pets/{id}` | Get pet details |
| PUT | `/api/v1/pets/{id}` | Update pet |
| DELETE | `/api/v1/pets/{id}` | Delete pet |

### Routine Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/routines/` | List all routine tasks |
| GET | `/api/v1/routines/pet/{pet_id}` | Get tasks for specific pet |
| POST | `/api/v1/routines/` | Create routine task |
| GET | `/api/v1/routines/task/{task_id}` | Get task details |
| PUT | `/api/v1/routines/task/{task_id}` | Update task |
| DELETE | `/api/v1/routines/task/{task_id}` | Delete task |

### Care History

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/logs/` | List all logs |
| GET | `/api/v1/logs/pet/{pet_id}` | Get logs for pet |
| GET | `/api/v1/logs/task/{task_id}` | Get logs for task |
| POST | `/api/v1/logs/` | Create log entry |
| DELETE | `/api/v1/logs/{id}` | Delete log |

### Admin Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/users/` | List all users |
| PATCH | `/api/v1/admin/users/{id}/activate` | Activate user |
| PATCH | `/api/v1/admin/users/{id}/deactivate` | Deactivate user |
| DELETE | `/api/v1/admin/users/{id}` | Delete user |
| GET | `/api/v1/admin/stats/` | System statistics |
| GET | `/api/v1/admin/settings/` | Get settings |
| PATCH | `/api/v1/admin/settings/{key}` | Update setting |

**Interactive API Documentation**: Visit `http://localhost:8000/docs` when the server is running.

---

## What's Intentionally Out of Scope

To keep LaNature focused and maintainable, the following features are **intentionally excluded** from the current version:

### **Not Included**

- **Mobile Apps**: Native iOS/Android apps (web-first approach)
- **Push Notifications**: Real-time notifications for care reminders
- **Veterinary Integration**: Direct integration with vet clinics or medical records
- **Social Features**: Sharing pet profiles, community features, or social media integration
- **Payment Processing**: Subscription management or payment gateways
- **Advanced Analytics**: Complex data visualization, predictive analytics, or AI insights
- **Multi-user Pet Sharing**: Multiple users managing the same pet (single-user accounts)
- **File Uploads**: Pet photos, medical documents, or file attachments
- **Calendar Integration**: Sync with Google Calendar, iCal, or other calendar systems
- **Email/SMS Reminders**: Automated email or SMS notifications
- **Pet Health Records**: Detailed medical history, vaccination tracking, or health metrics
- **Gamification**: Points, badges, or achievement systems

### **Why These Are Out of Scope**

- **Focus**: Core functionality (routines and tracking) is the priority
- **Simplicity**: Keeping the platform simple and easy to use
- **Maintainability**: Reducing complexity for easier maintenance
- **MVP Approach**: Building essential features first, expanding later based on user feedback

---

## Next Possible Evolutions

Based on user feedback and market needs, potential future enhancements include:

### **High Priority**

- **Mobile App**: Native iOS and Android applications for on-the-go access
- **Push Notifications**: Real-time reminders and notifications
- **Email Reminders**: Automated email notifications for upcoming care tasks
- **Photo Uploads**: Add photos to pets and care logs
- **Calendar Integration**: Sync with Google Calendar, Apple Calendar, etc.
- **Multi-user Support**: Share pet management with family members or pet sitters

### **Medium Priority**

- **Advanced Analytics**: Care pattern analysis, health trends, and insights
- **Veterinary Integration**: Connect with vet clinics and import medical records
- **Medication Tracking**: Detailed medication schedules, refill reminders, and dosage tracking
- **Health Metrics**: Weight tracking, activity monitoring, and health trends
- **Additional Languages**: Expand i18n support to more languages
- **Customizable Themes**: Dark mode and theme customization

### **Future Considerations**

- **AI-Powered Insights**: Predictive health analysis and care recommendations
- **IoT Integration**: Connect with smart feeders, water fountains, or activity trackers
- **Subscription Plans**: Premium features and subscription management
- **Telemedicine**: Integration with veterinary telemedicine services
- **Wearable Integration**: Connect with pet activity trackers and health monitors
- **API for Third-party**: Public API for integrations and third-party apps
- **Care Templates**: Pre-built care templates for common pet types and conditions
- **Export Data**: Export care history and reports (PDF, CSV)

### **Technical Improvements**

- **Docker Compose**: Complete development environment setup
- **Test Coverage**: Comprehensive unit and integration tests
- **Performance Optimization**: Caching, database optimization, CDN integration
- **Enhanced Security**: Two-factor authentication, rate limiting, security audits
- **PWA Support**: Progressive Web App capabilities
- **GraphQL API**: Alternative API interface option

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Author

**LaNature Team**

- GitHub: [@yourusername](https://github.com/yourusername)
- Email: contact@lanature.com

---

## Acknowledgments

- FastAPI community for the excellent framework
- React team for the amazing UI library
- All open-source contributors whose libraries made this project possible

---

<div align="center">

**Made with love for pet owners everywhere**

[Back to Top](#lanature---pet-care-management-saas)

</div>
