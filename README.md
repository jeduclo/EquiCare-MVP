# EquiCare MVP - Case Recording System

A secure, AI-powered case recording and management system for social workers.

## Features

- 🎙️ **Browser-based audio recording** (works on mobile & desktop)
- 🤖 **AI transcription** using OpenAI Whisper
- 📝 **AI-generated case summaries** using GPT-4
- 🔒 **Secure authentication** and encrypted storage
- 📱 **Mobile-responsive** interface
- 💾 **Case management** with search and filtering

## Quick Start

### 1. Setup Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# On Mac/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-actual-key-here
```

### 4. Initialize Database

```bash
python scripts/create_admin.py
```

This will create:
- The SQLite database
- An admin user (username: `admin`, password: `admin123`)

### 5. Run the Application

```bash
streamlit run src/app.py
```

The app will open in your browser at `http://localhost:8501`

## First Login

- **Username:** `admin`
- **Password:** `admin123`

**⚠️ IMPORTANT:** Change the admin password immediately after first login!

## Project Structure

```
EquiCare_MVP/
├── src/
│   ├── app.py              # Main application
│   ├── auth/               # Authentication
│   ├── database/           # Database models
│   ├── services/           # Business logic
│   └── ui/                 # User interface
├── data/                   # Local data storage
├── config.yaml             # App configuration
└── requirements.txt        # Dependencies
```

## Development

### Running Tests

```bash
pytest tests/
```

### Database Backup

```bash
python scripts/backup_db.py
```

## Deployment to Azure (Phase 2)

See `docs/DEPLOYMENT.md` for Azure deployment instructions.

## Tech Stack

- **Frontend:** Streamlit
- **Backend:** Python 3.10+
- **Database:** SQLite (MVP) → PostgreSQL (Production)
- **AI:** OpenAI (Whisper + GPT-4)
- **Authentication:** bcrypt + streamlit-authenticator

## Security

- Passwords hashed with bcrypt
- Audio files encrypted at rest
- Session-based authentication
- HTTPS required in production

## Support

For issues or questions, contact the development team.

## License

Proprietary - All rights reserved