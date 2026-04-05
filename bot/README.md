# CarBot - Refactored Structure

## 📁 Project Structure

```
carbot/
│
├── carbot-backend/        ← FastAPI Backend
│   ├── main.py           - API endpoints with Pydantic validation
│   ├── db.py             - Database connection
│   ├── migrate.py        - Database migration script
│   ├── migrations.sql    - SQL migration file
│   └── .env              - Environment variables
│
├── bot/                   ← Telegram Bot (Refactored)
│   ├── main.py           - Main application entry point
│   ├── config.py         - Configuration and environment variables
│   ├── states.py         - Conversation states
│   │
│   ├── services/
│   │   └── api.py        - API service layer (all backend calls)
│   │
│   ├── handlers/
│   │   ├── start.py      - /start command handler
│   │   ├── sell.py       - Sell flow (add car)
│   │   ├── search.py     - Search functionality
│   │   ├── listings.py   - Browse listings by brand
│   │   ├── mycars.py     - View user's cars
│   │   └── edit.py       - Edit car flow
│   │
│   └── keyboards/
│       ├── menus.py      - Reply keyboard markups
│       └── inline.py     - Inline keyboard markups
```

## 🚀 Running the Bot

### Backend
```bash
cd carbot-backend
python migrate.py  # Run migrations first
python main.py
```

### Bot
```bash
cd bot
python main.py
```

## ✨ What Changed

### Before (bot.py)
- Single 800+ line file
- Mixed concerns (API calls, keyboards, handlers)
- Hard to maintain and test
- Difficult to find specific functionality

### After (Modular Structure)
- **Separation of Concerns**: Each module has a single responsibility
- **Easy to Navigate**: Find handlers in `handlers/`, keyboards in `keyboards/`
- **Reusable Code**: API calls centralized in `services/api.py`
- **Testable**: Each module can be tested independently
- **Scalable**: Easy to add new features

## 📦 Module Responsibilities

### `config.py`
- Environment variables
- API URL configuration
- Bot token

### `states.py`
- All conversation states in one place
- Easy to see all possible states

### `services/api.py`
- All backend API calls
- Error handling for API requests
- Geocoding service

### `handlers/`
Each handler file contains:
- Command handlers
- Conversation flow logic
- State transitions

### `keyboards/`
- `menus.py`: Reply keyboards (main menu, brand selection, etc.)
- `inline.py`: Inline keyboards (buttons, pagination, actions)

### `main.py`
- Application setup
- Handler registration
- Conversation handler configuration
- Main entry point

## 🎯 Benefits

1. **Maintainability**: Easy to find and fix bugs
2. **Readability**: Clear module structure
3. **Reusability**: Shared code in services and keyboards
4. **Testability**: Each module can be unit tested
5. **Scalability**: Easy to add new features without touching existing code

## 🔧 Adding New Features

### Add a new command:
1. Create handler in `handlers/new_feature.py`
2. Import and register in `main.py`

### Add new keyboard:
1. Add function to `keyboards/menus.py` or `keyboards/inline.py`
2. Use in handlers

### Add new API endpoint:
1. Add function to `services/api.py`
2. Use in handlers

## 📝 Notes

- Old `bot.py` can be kept as backup or deleted
- All functionality preserved
- No breaking changes to user experience
- Backend remains unchanged
