# 🚗 CarBot - Telegram Car Marketplace Bot

A feature-rich Telegram bot for buying and selling cars, built with Python and FastAPI.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![python-telegram-bot](https://img.shields.io/badge/python--telegram--bot-20.0+-blue.svg)](https://python-telegram-bot.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://www.postgresql.org/)

## ✨ Features

### For Sellers
- 📝 **Easy Listing** - Step-by-step car listing process
- ✏️ **Edit Listings** - Menu-based editing of any field
- 🗑️ **Delete Listings** - Remove cars with confirmation
- 📍 **Location Support** - GPS or city name

### For Buyers
- 🔍 **Smart Search** - Search by brand or model
- 📋 **Browse by Brand** - Filter cars by manufacturer
- 📄 **Pagination** - Navigate through results easily
- 💰 **Detailed Info** - Price, mileage, description, location

### Technical Features
- ✅ **Input Validation** - Pydantic models with range checks
- 🔒 **Ownership Verification** - Users can only edit/delete their own cars
- 🚀 **Performance** - Database indexes for fast searches
- 🛡️ **Error Handling** - Detailed error messages
- 📱 **Clean UX** - Keyboard management, clear prompts

## 🏗️ Architecture

```
carbot/
├── carbot-backend/        # FastAPI REST API
│   ├── main.py           # API endpoints
│   ├── db.py             # Database connection
│   ├── migrate.py        # Migration script
│   └── migrations.sql    # SQL migrations
│
└── bot/                   # Telegram Bot
    ├── main.py           # Entry point
    ├── config.py         # Configuration
    ├── states.py         # Conversation states
    ├── services/         # Business logic
    ├── handlers/         # Command handlers
    └── keyboards/        # UI components
```

## 🚀 Quick Start

### Option 1: Docker (Recommended) 🐳

The easiest way to run CarBot:

```bash
# 1. Clone repository
git clone https://github.com/yourusername/carbot.git
cd carbot

# 2. Configure bot token
cd bot
cp .env.example .env
# Edit .env and add your BOT_TOKEN

# 3. Start everything
cd ..
docker-compose up --build

# 4. Run migrations (in new terminal)
docker exec -it carbot-backend python migrate.py
```

That's it! Your bot is now running. See [DOCKER.md](DOCKER.md) for detailed Docker instructions.

### Option 2: Manual Setup

<details>
<summary>Click to expand manual setup instructions</summary>

### Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Telegram Bot Token ([Get one from @BotFather](https://t.me/botfather))

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/carbot.git
cd carbot
```

### 2. Setup Database

```sql
CREATE DATABASE carbot;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE cars (
    id SERIAL PRIMARY KEY,
    make VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    year INTEGER NOT NULL,
    price INTEGER NOT NULL,
    mileage INTEGER NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    latitude FLOAT,
    longitude FLOAT,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
);
```

### 3. Run Migrations

```bash
cd carbot-backend
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DB_NAME=carbot
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
EOF

# Run migrations
python migrate.py
```

### 4. Start Backend

```bash
cd carbot-backend
uvicorn main:app --reload
```

Backend will run on `http://localhost:8000`

### 5. Start Bot

```bash
cd bot
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
BOT_TOKEN=your_telegram_bot_token_here
EOF

# Run bot
python main.py
```

</details>

## 🐳 Docker

### Services

- **PostgreSQL** - Database (port 5432)
- **FastAPI Backend** - REST API (port 8000)
- **Telegram Bot** - Bot application

### Commands

```bash
# Start all services
docker-compose up --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Run migrations
docker exec -it carbot-backend python migrate.py
```

See [DOCKER.md](DOCKER.md) for complete Docker documentation.

## 📦 Dependencies

### Backend
```txt
fastapi==0.100.0
uvicorn==0.23.0
psycopg2-binary==2.9.6
pydantic==2.0.0
python-dotenv==1.0.0
```

### Bot
```txt
python-telegram-bot==20.3
requests==2.31.0
python-dotenv==1.0.0
```

## 🎮 Usage

### Commands

- `/start` - Start the bot and show main menu
- `/sell` - List a new car for sale
- `/search <query>` - Search for cars (e.g., `/search toyota`)
- `/listings` - Browse cars by brand
- `/mycars` - View your listed cars

### Main Menu

```
[Sell 🚗]  [Listings 📋]
[Search 🔍] [My Cars 👤]
```

### Sell Flow

1. Choose brand (Toyota, BMW, Mercedes, Opel, or Other)
2. Enter model
3. Enter year
4. Enter price
5. Enter mileage
6. Enter description
7. Send location (GPS or city name)

### Edit Flow

1. Go to "My Cars 👤"
2. Click "✏️ Edit" on any car
3. Select field to edit from menu
4. Enter new value
5. Click "✅ Save Changes"

## 🔧 Configuration

### Backend (`carbot-backend/.env`)

```env
DB_NAME=carbot
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
```

### Bot (`bot/.env`)

```env
BOT_TOKEN=your_telegram_bot_token
```

## 🗄️ Database Schema

### Users Table
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| telegram_id | BIGINT | Telegram user ID (unique) |
| name | VARCHAR(255) | User's first name |

### Cars Table
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| make | VARCHAR(50) | Car brand |
| model | VARCHAR(50) | Car model |
| year | INTEGER | Manufacturing year |
| price | INTEGER | Price in USD |
| mileage | INTEGER | Mileage in km |
| description | TEXT | Car description |
| created_at | TIMESTAMP | Creation timestamp |
| latitude | FLOAT | Location latitude |
| longitude | FLOAT | Location longitude |
| user_id | INTEGER | Foreign key to users |

## 🔒 Security Features

- ✅ Input validation with Pydantic
- ✅ SQL injection prevention (parameterized queries)
- ✅ Ownership verification for edit/delete
- ✅ Proper HTTP status codes (403, 404, 500)
- ✅ Database constraints (NOT NULL, CHECK, FOREIGN KEY)

## 🚀 Performance Optimizations

- 📊 Database indexes on `make`, `model`, `user_id`
- 🔍 Trigram indexes for fast ILIKE searches
- 📄 Pagination (5 results per page)
- ⚡ Connection pooling ready

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [python-telegram-bot](https://python-telegram-bot.org/) - Telegram Bot API wrapper
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [PostgreSQL](https://www.postgresql.org/) - Database
- [Nominatim](https://nominatim.org/) - Geocoding service

## 📧 Contact

Your Name - [@@Ilyas_Yahshimuratow](https://t.me/Ilyas_Yahshimuratow)

Project Link: [https://github.com/yourusername/carbot](https://github.com/yourusername/carbot)

---

Made with ❤️ and Python
