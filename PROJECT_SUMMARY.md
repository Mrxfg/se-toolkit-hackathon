# 🚗 CarBot - Project Summary

## 📌 Problem Statement

Buying and selling cars through traditional online platforms often involves:

- **Privacy Concerns** - Exposing personal phone numbers and contact information publicly
- **Platform Fragmentation** - Switching between multiple apps for browsing, messaging, and negotiating
- **Poor User Experience** - Complex interfaces with unnecessary features
- **Limited Communication** - No built-in messaging, forcing users to external platforms
- **Trust Issues** - Difficulty verifying sellers and establishing trust

**The Challenge:** Create a simple, secure, and integrated platform for car marketplace transactions that prioritizes user privacy and seamless communication.

---

## 💡 Solution

**CarBot** is a Telegram-based car marketplace bot that provides:

✅ **All-in-One Platform** - Browse, list, and communicate within Telegram  
✅ **Privacy-First** - No phone numbers or personal contact info exposed  
✅ **In-Bot Messaging** - Direct buyer-seller communication without leaving the app  
✅ **Simple Interface** - Intuitive keyboard navigation and clear workflows  
✅ **Photo Support** - Upload and view up to 5 photos per listing  
✅ **Location-Based** - GPS or city-based location for each listing  
✅ **Instant Notifications** - Real-time alerts for messages and inquiries  

---

## ✨ Key Features

### Version 1.0 (Current - April 2026)

#### Core Functionality
- **Car Listings** - Add, edit, and delete car listings with full CRUD operations
- **Photo Management** - Upload up to 5 photos per car, with individual deletion
- **Search & Browse** - Search by brand/model or browse by manufacturer
- **Location Support** - GPS coordinates or city name for each listing
- **Pagination** - Navigate through large result sets efficiently

#### Messaging System
- **Contact Seller** - Send messages to car owners without exposing contact info
- **Inbox** - View all received messages with read/unread status
- **Reply Functionality** - Sellers can reply directly from inbox
- **Instant Notifications** - Both parties receive real-time message alerts
- **Conversation Context** - Messages always show which car they're about

#### User Management
- **Authentication** - Automatic user registration via Telegram
- **Ownership Verification** - Users can only edit/delete their own listings
- **My Cars** - View and manage all your listed vehicles

#### Technical Features
- **Input Validation** - Pydantic models ensure data integrity
- **Database Indexes** - Optimized queries for fast search
- **Error Handling** - Graceful failures with user-friendly messages
- **Docker Support** - One-command deployment with docker-compose
- **RESTful API** - Clean FastAPI backend with auto-generated docs

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework for building APIs
- **PostgreSQL** - Robust relational database for data storage
- **Pydantic** - Data validation and settings management
- **psycopg2** - PostgreSQL adapter for Python
- **Uvicorn** - ASGI server for FastAPI

### Bot
- **python-telegram-bot** - Telegram Bot API wrapper
- **Requests** - HTTP library for API communication
- **python-dotenv** - Environment variable management

### Infrastructure
- **Docker** - Containerization for consistent deployments
- **Docker Compose** - Multi-container orchestration
- **PostgreSQL 15** - Database container
- **Python 3.12** - Runtime environment

### Development Tools
- **Git** - Version control
- **GitHub** - Code hosting and collaboration
- **Swagger/ReDoc** - Auto-generated API documentation

---

## 🏗️ Architecture Overview

CarBot follows a **three-tier microservices architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│                    Telegram Users                            │
│              (Buyers and Sellers)                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Telegram Bot Layer                         │
│  • Handles user interactions                                 │
│  • Manages conversation states                               │
│  • Provides keyboard navigation                              │
│  • Sends notifications                                       │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend                            │
│  • Business logic                                            │
│  • Data validation (Pydantic)                                │
│  • Authentication & authorization                            │
│  • Image processing                                          │
└────────────────────────┬────────────────────────────────────┘
                         │ SQL
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  PostgreSQL Database                         │
│  • Users table                                               │
│  • Cars table                                                │
│  • Car_images table (BYTEA storage)                          │
│  • Messages table                                            │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

**1. Telegram Bot (Frontend)**
- User interface and interaction
- Conversation flow management
- Command handling (/start, /sell, /search, etc.)
- Inline and reply keyboard management
- Real-time notifications

**2. FastAPI Backend (Business Logic)**
- RESTful API endpoints
- Request validation with Pydantic
- Business rules enforcement
- Image compression and storage
- Error handling and logging

**3. PostgreSQL Database (Data Layer)**
- Persistent data storage
- Relational data integrity
- Full-text search (pg_trgm extension)
- Foreign key constraints with CASCADE
- Indexed queries for performance

---

## 📊 Database Schema

### Tables

**users**
```sql
id              SERIAL PRIMARY KEY
telegram_id     BIGINT UNIQUE NOT NULL
name            VARCHAR(255) NOT NULL
telegram_username VARCHAR(255)
created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

**cars**
```sql
id              SERIAL PRIMARY KEY
make            VARCHAR(50) NOT NULL
model           VARCHAR(50) NOT NULL
year            INTEGER NOT NULL CHECK (year >= 1900 AND year <= 2100)
price           INTEGER NOT NULL CHECK (price > 0)
mileage         INTEGER NOT NULL CHECK (mileage >= 0)
description     TEXT NOT NULL
latitude        FLOAT CHECK (latitude >= -90 AND latitude <= 90)
longitude       FLOAT CHECK (longitude >= -180 AND longitude <= 180)
user_id         INTEGER REFERENCES users(id) ON DELETE CASCADE
created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

**car_images**
```sql
id              SERIAL PRIMARY KEY
car_id          INTEGER NOT NULL REFERENCES cars(id) ON DELETE CASCADE
image_data      BYTEA NOT NULL
image_order     INTEGER DEFAULT 0
uploaded_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

**messages**
```sql
id              SERIAL PRIMARY KEY
car_id          INTEGER NOT NULL REFERENCES cars(id) ON DELETE CASCADE
from_user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE
to_user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE
message_text    TEXT NOT NULL
is_read         BOOLEAN DEFAULT FALSE
created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

---

## 🎯 Future Roadmap

### Version 2.0 (Q3 2026)

#### Favorites System
- Save favorite car listings
- Quick access to saved cars
- Favorite count per listing
- Remove from favorites

#### Advanced Search
- **Price Range Filter** - Min/max price selection
- **Year Range Filter** - Filter by manufacturing year
- **Mileage Filter** - Set maximum mileage
- **Location-Based Search** - Find cars within X km radius
- **Sort Options** - By price, date, mileage, distance

#### Notifications
- **Price Drop Alerts** - Get notified when favorited cars drop in price
- **New Listings** - Alerts for new cars matching your preferences
- **Message Notifications** - Enhanced push notifications
- **Listing Expiration** - Reminders to renew old listings

#### Analytics & Insights
- **View Count** - Track how many people viewed your listing
- **Response Rate** - See how quickly you respond to messages
- **Popular Listings** - Trending cars and brands
- **Seller Dashboard** - Statistics for your listings

### Version 3.0 (2027)

#### Social Features
- **User Ratings** - Rate buyers and sellers (1-5 stars)
- **Reviews** - Written feedback for transactions
- **Verified Sellers** - Badge system for trusted users
- **Seller Profiles** - View seller's history and ratings

#### Advanced Features
- **AI Price Recommendations** - ML-based pricing suggestions
- **Car Condition Assessment** - AI analysis of uploaded photos
- **Multi-Language Support** - English, Russian, Uzbek, Turkish
- **Payment Integration** - Secure in-app deposits/payments
- **Car History Reports** - Integration with vehicle history APIs

#### Platform Expansion
- **Web Interface** - Responsive web app for desktop users
- **Mobile App** - Native iOS/Android apps (React Native)
- **Admin Dashboard** - Moderation and analytics panel
- **API for Partners** - Public API for third-party integrations

---

## 📈 Project Metrics

### Current Status (Version 1.0)

- **Lines of Code:** ~3,500
- **API Endpoints:** 20+
- **Database Tables:** 4
- **Bot Commands:** 6
- **Conversation Flows:** 3 (Sell, Edit, Message)
- **Docker Containers:** 3
- **Development Time:** 2 weeks
- **Test Coverage:** Manual testing (automated tests planned for v2.0)

### Performance Targets

- **Response Time:** < 500ms for API calls
- **Bot Response:** < 2 seconds for user interactions
- **Image Upload:** < 5 seconds per photo
- **Search Results:** < 1 second for queries
- **Concurrent Users:** 100+ simultaneous users

---

## 🎓 Learning Outcomes

This project demonstrates proficiency in:

### Backend Development
- RESTful API design with FastAPI
- Database schema design and optimization
- Data validation with Pydantic
- SQL queries and database indexing
- Image storage and processing

### Bot Development
- Telegram Bot API integration
- Conversation state management
- Inline and reply keyboard design
- Real-time notifications
- User experience optimization

### DevOps & Deployment
- Docker containerization
- Docker Compose orchestration
- Environment configuration
- Database migrations
- Service networking

### Software Engineering
- Clean code architecture
- Modular design patterns
- Error handling strategies
- Security best practices
- Documentation writing

---

## 🚀 Deployment

### Development
```bash
docker-compose up --build
docker exec -it carbot-backend python migrate.py
```

### Production Considerations
- Use managed PostgreSQL (AWS RDS, DigitalOcean)
- Deploy backend on cloud platform (Heroku, Railway, Render)
- Configure SSL/TLS for API
- Set up monitoring (Prometheus, Grafana)
- Implement logging (ELK stack)
- Use secrets management (Vault, AWS Secrets Manager)
- Configure auto-scaling for high traffic

---

## 🔒 Security Features

- ✅ **No Exposed Credentials** - Telegram IDs never shown to users
- ✅ **SQL Injection Prevention** - Parameterized queries
- ✅ **Input Validation** - Pydantic models with constraints
- ✅ **Ownership Verification** - Users can only modify their own data
- ✅ **Environment Variables** - Secrets stored in .env files
- ✅ **Database Constraints** - Foreign keys and CHECK constraints
- ✅ **Error Handling** - No sensitive data in error messages

---

## 🤝 Contributing

This project is open for contributions! Areas where help is needed:

- [ ] Unit and integration tests
- [ ] Frontend web interface
- [ ] Mobile app development
- [ ] Multi-language support
- [ ] Performance optimization
- [ ] Documentation improvements

---

## 📞 Contact & Links

**Developer:** Ilyas Yahshimuratov

- **Telegram:** [@Ilyas_Yahshimuratow](https://t.me/Ilyas_Yahshimuratow)
- **GitHub:** [@Mrxfg](https://github.com/Mrxfg)
- **Project Repository:** [se-toolkit-hackathon](https://github.com/Mrxfg/se-toolkit-hackathon)
- **Live Bot:** [@Carsallesbot](https://t.me/Carsallesbot)

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Special thanks to:
- **Anthropic** - For Claude AI assistance in development
- **Telegram** - For the Bot API platform
- **FastAPI Community** - For excellent documentation
- **PostgreSQL Team** - For the robust database
- **Open Source Community** - For the amazing tools and libraries

---

**Made with ❤️ and Python**

*Project completed: April 2026*
