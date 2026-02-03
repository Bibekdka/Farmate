# 🌾 FarmApp - Agricultural Management System

## ✅ Current Stable Version

This version includes all working features with automatic data protection.

### 🎯 Core Features:
- **Dashboard**: Financial tracking with grouped records by date
- **Calendar**: Monthly view with activities and reminders
- **Weather**: Live forecast + historical data
- **Crops & Yield**: Crop management and yield tracking
- **Disease Log**: Track and manage crop diseases
- **AI Assistant**: Gemini-powered farming advice
- **Knowledge Hub**: Pest control, crop calendars, turmeric data
- **Reminders**: Task management system
- **Reports**: Comprehensive financial and yield reports

### 🔒 Data Protection (5-Layer Backup):
1. **Auto-backup**: After every data change
2. **Daily backup**: Scheduled at 11 PM
3. **Manual backup**: Run `python backup_db.py`
4. **Cloud backup**: Google Sheets integration (optional)
5. **Production backup**: Render PostgreSQL daily backups

### 📊 Live Status Indicator:
Check the sidebar on any page for:
- 💾 Data Protection status
- ✅ Auto-backup confirmation
- 📅 Last backup timestamp

### 🚀 Running the Application:

**Local Development:**
```bash
python app.py
```
Access at: http://127.0.0.1:5000

**Production (Render):**
- URL: [Your Render deployment URL]
- Database: PostgreSQL (automatic backups)
- Python: 3.11.9

### 📁 Project Structure:
```
Agriculture/
├── app.py                      # Main application
├── config.py                   # Configuration
├── wsgi.py                     # Production entry point
├── ai_service.py               # AI integration
├── backup_db.py                # Multi-location backup
├── backup_to_sheets.py         # Google Sheets backup
├── check_latest_data.py        # Auto-restore latest data
├── add_historical_weather.py   # Weather data recovery
├── templates/                  # HTML templates
├── data/                       # Knowledge base JSON files
├── instance/                   # SQLite database
└── backups/                    # Local backups
```

### 🛠️ Maintenance:

**Create Backup:**
```bash
python backup_db.py
```

**Check for Latest Data:**
```bash
python check_latest_data.py
```

**Export to Google Sheets:**
```bash
python backup_to_sheets.py
```

### 🔐 Environment Variables:
```env
DATABASE_URL=postgresql://...  # Production only
SECRET_KEY=your-secret-key
GEMINI_API_KEY=your-api-key
FARM_LATITUDE=26.1445
FARM_LONGITUDE=91.7362
```

### 📦 Dependencies:
- Flask 3.1.0
- SQLAlchemy 2.0.36
- PostgreSQL (production) / SQLite (development)
- Gunicorn (production server)
- See `requirements.txt` for complete list

### ✨ Recent Improvements:
- ✅ Fixed calendar datetime issues
- ✅ Added live backup status indicator
- ✅ Grouped dashboard records by date
- ✅ Added daily summaries per date
- ✅ Multi-location automatic backups
- ✅ Auto-restore latest data on startup
- ✅ Python 3.11.9 for compatibility

### 🐛 Known Issues:
None currently - all features working!

### 📞 Support:
For issues or questions, check:
- `BACKUP_README.md` - Complete backup system documentation
- GitHub repository commit history
- Render deployment logs

---

**Last Updated:** 2026-02-03
**Version:** 1.1 (Stable)
**Status:** ✅ Production Ready
