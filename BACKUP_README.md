# 🔒 FarmApp Data Backup System

## ✅ Your Data is Now TRIPLE Protected!

### 1. **Automatic Backups** (Every Time You Save Data)
- Backup happens automatically after every database change
- Stored in: `backups/auto_backup_TIMESTAMP.db`
- Keeps last 20 auto-backups

### 2. **Multi-Location Manual Backup**
Run this command anytime:
```bash
python backup_db.py
```

**Backup Locations:**
1. ✅ **Local**: `backups/farm_data_TIMESTAMP.db`
2. ✅ **OneDrive**: `OneDrive/FarmApp_Backups/YYYY-MM-DD/`
3. ✅ **Desktop**: `Desktop/FarmApp_Emergency_Backups/YYYY-MM-DD/`

### 3. **Daily Scheduled Backup** (Windows)
Just double-click: `run_daily_backup.bat`

Or set up Windows Task Scheduler:
1. Open Task Scheduler
2. Create Basic Task
3. Name: "FarmApp Daily Backup"
4. Trigger: Daily at 11:00 PM
5. Action: Start `run_daily_backup.bat`

---

## ☁️ Google Sheets Cloud Backup (Optional)

Want to backup to Google Sheets? Follow these steps:

### Setup (One-Time):
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable **Google Sheets API**
4. Create Service Account credentials
5. Download JSON file as `google_sheets_credentials.json`
6. Place it in the FarmApp folder
7. Install libraries:
```bash
pip install gspread oauth2client
```

### Run Backup to Google Sheets:
```bash
python backup_to_sheets.py
```

Your data will be exported to a Google Sheet that you can access from anywhere!

---

## 🚨 In Case of Data Loss

### Option 1: Restore from Local Backup
1. Go to `backups/` folder
2. Find the latest `farm_data_TIMESTAMP.db` or `auto_backup_TIMESTAMP.db`
3. Copy it to `instance/farm_data.db`
4. Restart the app

### Option 2: Restore from OneDrive
1. Go to `OneDrive/FarmApp_Backups/`
2. Find today's date folder
3. Copy the `.db` file to `instance/farm_data.db`

### Option 3: Restore from Desktop
1. Go to `Desktop/FarmApp_Emergency_Backups/`
2. Same as Option 2

### Option 4: Restore from Google Sheets
- Your data is viewable/exportable from the Google Sheet
- Can be manually re-imported or downloaded as CSV

---

## 📊 Production Database (Render)

Your production app uses **PostgreSQL** on Render:
- Automatic backups by Render (daily)
- Download from Render Dashboard → Database → Backups
- No risk of data loss on production!

---

## 🛡️ Data Safety Checklist

✅ Automatic backup on every save  
✅ 3 backup locations (Local + OneDrive + Desktop)  
✅ Daily scheduled backup (via .bat file)  
✅ Google Sheets cloud backup (optional)  
✅ Production PostgreSQL with Render backups  
✅ Backup manifest tracking  

**Your data is now BULLETPROOF!** 🔐

---

## Quick Commands Reference

```bash
# Manual backup to 3 locations
python backup_db.py

# Backup to Google Sheets (if configured)
python backup_to_sheets.py

# Add historical weather data
python add_historical_weather.py

# Run the app locally
python app.py
```

---

## Support

If you lose data:
1. **DON'T PANIC!** Your data is backed up in 3+ places
2. Check the `backups/` folder first
3. Check OneDrive and Desktop backup folders
4. Contact support with timestamp of lost data

**Last Updated:** 2026-02-03
