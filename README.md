# 🚗 CarBot - Telegram Car Marketplace

A feature-rich Telegram bot for buying and selling cars, built with Python, FastAPI, and PostgreSQL. CarBot provides a seamless experience for users to list their vehicles, search for cars, and communicate with sellers directly within Telegram.

**🤖 Try it live:** [@Carsallesbot](https://t.me/Carsallesbot)

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Screenshots](#-screenshots)
- [Quick Start](#-quick-start)
- [Setup Instructions](#-setup-instructions)
- [Usage](#-usage)
- [Environment Variables](#-environment-variables)
- [API Documentation](#-api-documentation)
- [Project Versions](#-project-versions)
- [Future Improvements](#-future-improvements)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### Version 1 (Current)

#### For Sellers
- 📝 **Easy Listing** - Step-by-step car listing with validation
- 📸 **Photo Upload** - Add up to 5 photos per listing
- ✏️ **Edit Listings** - Update any field including photos
- 🗑️ **Delete Listings** - Remove cars with confirmation
- 📍 **Location Support** - GPS coordinates or city name
- 💬 **Inbox System** - Receive and reply to buyer messages

#### For Buyers
- 🔍 **Smart Search** - Search by brand or model
- 📋 **Browse by Brand** - Filter cars by manufacturer
- 📄 **Pagination** - Navigate through results easily
- 💰 **Detailed Info** - Price, mileage, description, photos, location
- 📞 **Contact Seller** - Send messages directly through the bot
- 📬 **Message Inbox** - View and manage conversations

#### Technical Features
- ✅ **Input Validation** - Pydantic models with range checks
- 🔒 **Ownership Verification** - Users can only edit/delete their own cars
- 💬 **In-Bot Messaging** - Private communication without exposing contact info
- 🚀 **Performance** - Database indexes for fast searches
- 🛡️ **Error Handling** - Detailed error messages and graceful failures
- 📱 **Clean UX** - Intuitive keyboard navigation and clear prompts
- 🐳 **Docker Support** - One-command deployment

### Version 2 (Planned)
- ❤️ **Favorites** - Save and manage favorite listings
- 🔔 **Notifications** - Price drops and new listings alerts
- 🎯 **Advanced Search** - Filter by price range, year, mileage, location
- 📊 **Analytics** - View statistics for your listings
- ⭐ **Ratings** - Rate buyers and sellers
- 🔐 **Verified Sellers** - Badge system for trusted users

---

## 🏗️ Architecture

CarBot follows a modern microservices architecture with three main components:

```
┌─────────────────────────────────────────────────────────────┐
│                         Telegram Bot                         │
│  (python-telegram-bot - Handles user interactions)          │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP Requests
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                         │
│  (REST API - Business logic & data validation)              │
└────────────────────────┬────────────────────────────────────┘
                         │ SQL Queries
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                       │
│  (Data storage - Users, Cars, Images, Messages)             │
└─────────────────────────────────────────────────────────────┘
```

### Project Structure

```
carbot/
├── bot/                      # Telegram Bot Application
│   ├── handlers/            # Command and callback handlers
│   │   ├── start.py        # /start command
│   │   ├── sell.py         # Car listing flow
│   │   ├── search.py       # Search functionality
│   │   ├── listings.py     # Browse by brand
│   │   ├── mycars.py       # User's car management
│   │   └── edit.py         # Edit car details
│   ├── services/           # Business logic
│   │   └── api.py          # Backend API client
│   ├── keyboards/          # UI components
│   │   ├── menus.py        # Reply keyboards
│   │   └── inline.py       # Inline keyboards
│   ├── helpers/            # Utility functions
│   │   └── display.py      # Car display with photos
│   ├── main.py             # Bot entry point
│   ├── config.py           # Configuration
│   ├── states.py           # Conversation states
│   └── requirements.txt    # Python dependencies
│
├── carbot-backend/          # FastAPI Backend
│   ├── main.py             # API endpoints
│   ├── db.py               # Database connection
│   ├── migrate.py          # Database migrations
│   ├── migrations.sql      # SQL migration scripts
│   └── requirements.txt    # Python dependencies
│
├── docker-compose.yml       # Docker orchestration
├── .gitignore              # Git ignore rules
├── README.md               # This file
├── DOCKER.md               # Docker documentation
└── PROJECT_SUMMARY.md      # Project overview
```

---

## 📸 Screenshots

> **Note:** Add screenshots here to showcase your bot's interface

```
[Screenshot 1: Main Menu]
[Screenshot 2: Car Listing with Photos]
[Screenshot 3: Search Results]
[Screenshot 4: Inbox Messages]
```

---

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/Mrxfg/se-toolkit-hackathon.git
cd carbot

# 2. Configure environment variables
cp bot/.env.example bot/.env
# Edit bot/.env and add your BOT_TOKEN

# 3. Start all services
docker-compose up --build

# 4. Run database migrations (in a new terminal)
docker exec -it carbot-backend python migrate.py
```

That's it! Your bot is now running at [@Carsallesbot](https://t.me/Carsallesbot)

For detailed Docker instructions, see [DOCKER.md](DOCKER.md)

---

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.12+
- PostgreSQL 13+
- Docker & Docker Compose (for containerized setup)
- Telegram Bot Token ([Get one from @BotFather](https://t.me/botfather))

### Option 1: Docker Setup (Recommended)

See [Quick Start](#-quick-start) above.

### Option 2: Local Development Setup

#### 1. Clone Repository

```bash
git clone https://github.com/Mrxfg/se-toolkit-hackathon.git
cd carbot
```

#### 2. Setup PostgreSQL Database

```bash
# Create database
createdb carbot

# Or using psql
psql -U postgres
CREATE DATABASE carbot;
\q
```

#### 3. Setup Backend

```bash
cd carbot-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cat > .env << EOF
DB_NAME=carbot
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
EOF

# Run migrations
python migrate.py

# Start backend server
uvicorn main:app --reload
```

Backend will run on `http://localhost:8000`

#### 4. Setup Bot

```bash
cd ../bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cat > .env << EOF
BOT_TOKEN=your_telegram_bot_token_here
API_URL=http://localhost:8000
EOF

# Start bot
python main.py
```

---

## 📱 Usage

### Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and show main menu |
| `/sell` | List a new car for sale |
| `/search <query>` | Search for cars (e.g., `/search toyota`) |
| `/listings` | Browse cars by brand |
| `/mycars` | View and manage your listed cars |
| `/inbox` | View messages from buyers/sellers |

### Main Menu

```
[Sell 🚗]     [Listings 📋]
[Search 🔍]   [My Cars 👤]
[Inbox 📬]
```

### User Flows

#### Selling a Car

1. Click "Sell 🚗" or use `/sell`
2. Select brand (Toyota, BMW, Mercedes, Opel, or Other)
3. Enter model name
4. Enter year (1900-2100)
5. Enter price (USD)
6. Enter mileage (km)
7. Enter description
8. Send location (GPS or city name)
9. Upload photos (up to 5, optional)
10. Car is listed!

#### Searching for Cars

1. Click "Search 🔍" or use `/search toyota`
2. View results with photos
3. Click "📞 Contact Seller" to message the owner
4. Type your message
5. Seller receives notification and can reply via inbox

#### Managing Your Cars

1. Click "My Cars 👤" or use `/mycars`
2. View all your listings with photos
3. Click "✏️ Edit" to modify any field
4. Click "❌ Delete" to remove a listing

#### Messaging System

**For Buyers:**
1. Find a car you like
2. Click "📞 Contact Seller"
3. Click "💬 Send Message"
4. Type your message
5. Seller receives instant notification

**For Sellers:**
1. Receive notification when someone messages you
2. Use `/inbox` or click "Inbox 📬"
3. View all messages
4. Click "↩️ Reply" to respond
5. Buyer receives your reply instantly

---

## 🔧 Environment Variables

### Backend (`carbot-backend/.env`)

```env
DB_NAME=carbot
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
```

### Bot (`bot/.env`)

```env
BOT_TOKEN=your_telegram_bot_token_from_botfather
API_URL=http://localhost:8000
```

### Docker Compose (`.env` in root)

```env
DB_PASSWORD=your_secure_password
```

> **Security Note:** Never commit `.env` files to Git. Use `.env.example` as a template.

---

## 📚 API Documentation

Once the backend is running, visit:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

### Key Endpoints

#### Users
- `POST /users` - Create or get user
- `PUT /users` - Update user information

#### Cars
- `POST /cars` - Add a new car listing
- `GET /cars` - Get all cars (with pagination)
- `GET /cars/search?q=toyota` - Search cars
- `GET /cars/brands` - Get all brands
- `GET /cars/user/{telegram_id}` - Get user's cars
- `PUT /cars/{car_id}` - Update a car
- `DELETE /cars/{car_id}` - Delete a car
- `GET /cars/{car_id}/seller` - Get seller information

#### Images
- `POST /cars/{car_id}/images` - Upload car image
- `GET /cars/{car_id}/images` - Get all car images
- `DELETE /cars/{car_id}/images/{image_id}` - Delete an image

#### Messages
- `POST /messages` - Send a message
- `GET /messages/inbox/{telegram_id}` - Get user's inbox
- `PUT /messages/{message_id}/read` - Mark message as read

---

## 📦 Project Versions

### Version 1.0 (Current - April 2026)

**Status:** ✅ Production Ready

**Features:**
- Complete CRUD operations for car listings
- Photo upload and management (up to 5 per car)
- Search and browse functionality
- In-bot messaging system
- User authentication and authorization
- Docker deployment

**Tech Stack:**
- Python 3.12
- FastAPI 0.100+
- python-telegram-bot 20.3
- PostgreSQL 13+
- Docker & Docker Compose

### Version 2.0 (Planned - Q3 2026)

**Planned Features:**
- Favorites system
- Advanced search filters (price range, year, mileage, location)
- Push notifications for price drops
- User ratings and reviews
- Verified seller badges
- Analytics dashboard
- Multi-language support

---

## 🚀 Future Improvements

### Short-term (1-3 months)
- [ ] Add favorites functionality
- [ ] Implement advanced search filters
- [ ] Add price drop notifications
- [ ] Create admin dashboard
- [ ] Add unit and integration tests

### Mid-term (3-6 months)
- [ ] User rating system
- [ ] Verified seller badges
- [ ] Analytics for sellers
- [ ] Mobile-responsive web interface
- [ ] Payment integration

### Long-term (6-12 months)
- [ ] AI-powered price recommendations
- [ ] Car condition assessment via photos
- [ ] Multi-language support
- [ ] Integration with car valuation APIs
- [ ] Mobile app (React Native)

---

## 🗄️ Database Schema

### Tables

**users**
- `id` - Primary key
- `telegram_id` - Unique Telegram user ID
- `name` - User's first name
- `telegram_username` - Telegram username
- `created_at` - Registration timestamp

**cars**
- `id` - Primary key
- `make` - Car brand
- `model` - Car model
- `year` - Manufacturing year (1900-2100)
- `price` - Price in USD (> 0)
- `mileage` - Mileage in km (>= 0)
- `description` - Car description
- `latitude` - Location latitude
- `longitude` - Location longitude
- `user_id` - Foreign key to users
- `created_at` - Listing timestamp

**car_images**
- `id` - Primary key
- `car_id` - Foreign key to cars (CASCADE delete)
- `image_data` - Binary image data (BYTEA)
- `image_order` - Display order (0-4)
- `uploaded_at` - Upload timestamp

**messages**
- `id` - Primary key
- `car_id` - Foreign key to cars (CASCADE delete)
- `from_user_id` - Foreign key to users (sender)
- `to_user_id` - Foreign key to users (recipient)
- `message_text` - Message content
- `is_read` - Read status
- `created_at` - Message timestamp

---

## 🔒 Security Features

- ✅ SQL injection prevention (parameterized queries)
- ✅ Input validation with Pydantic models
- ✅ Ownership verification for edit/delete operations
- ✅ Private messaging (no contact info exposed)
- ✅ Environment variables for secrets
- ✅ Database constraints and foreign keys
- ✅ Proper HTTP status codes (403, 404, 500)

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide for Python code
- Write clear commit messages
- Add comments for complex logic
- Update documentation for new features
- Test your changes before submitting

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [python-telegram-bot](https://python-telegram-bot.org/) - Telegram Bot API wrapper
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [PostgreSQL](https://www.postgresql.org/) - Powerful database
- [Nominatim](https://nominatim.org/) - Geocoding service

---

## 📧 Contact

**Developer:** Ilyas Yahshimuratov

- Telegram: [@Ilyas_Yahshimuratow](https://t.me/Ilyas_Yahshimuratow)
- GitHub: [@Mrxfg](https://github.com/Mrxfg)
- Project Link: [https://github.com/Mrxfg/se-toolkit-hackathon](https://github.com/Mrxfg/se-toolkit-hackathon)

---

## ⭐ Show Your Support

If you found this project helpful, please give it a ⭐ on GitHub!

---

*Last updated: April 2026*
