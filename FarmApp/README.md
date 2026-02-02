# Farmate

A comprehensive, mobile-responsive web application for modern farmers to track finances, crops, yields, diseases, and farming activities.

## ✨ Features

### 📊 **Dashboard**
- Real-time financial overview (Income, Expenses, Profit)
- Expense breakdown by category (Fuel, Labour, Food, Transportation, Misc)
- Visual charts and analytics
- Add backdated records

### 🚜 **Crop Management**
- Track multiple crops with variety and season info
- Monitor crop health status
- Link crops to yield and disease logs
- View crop performance metrics

### 🌾 **Yield Tracking**
- Log crop production with multiple units (kg, quintal, tons, grams)
- Automatic conversion to kg for standardized tracking
- Historical yield data and trends
- Production statistics

### 🦠 **Disease & Pest Logging**
- Record diseases/pests with severity levels (Mild, Moderate, Severe)
- Track affected area percentages
- Document treatments and observations
- Quick access to treatment history

### 📅 **Calendar View**
- Monthly calendar with color-coded events
- View all farm activities and reminders in one place
- Easy date-based navigation

### 📋 **Task Management**
- Create reminders with priority levels (Low, Normal, High)
- Mark tasks as complete
- View upcoming and completed reminders
- Never miss important farm activities

### 📈 **Reports & Analytics**
- Monthly financial breakdown
- Activity-wise expense analysis
- Disease statistics and severity trends
- Total yield production tracking
- Export-ready data visualization

### 📝 **Notes**
- Quick note-taking for farm observations
- Timestamped entries
- Full edit/delete capabilities

---

## 🛠️ Tech Stack

- **Backend:** Flask (Python 3.10+)
- **Database:** SQLAlchemy + SQLite
- **Frontend:** Bootstrap 5.3 + Chart.js
- **Server:** Gunicorn (Production)
- **Weather API:** OpenWeatherMap (Optional)

---

## 📦 Installation

### Quick Start (Development)

```bash
# Clone/download the project
cd FarmApp

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\Activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Run application
python app.py

# Open browser: http://localhost:5000
```

### Production Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for:
- Windows Server with IIS
- Linux with Nginx + Gunicorn
- Heroku deployment
- PythonAnywhere setup
- Security checklist
- Monitoring & backups

---

## 📋 Database Schema

### **FarmRecord**
- Financial transactions (income/expenses)
- Activity tracking
- Category and expense type

### **Crop**
- Crop details (name, variety, season, area)
- Sowing and harvest dates
- Status tracking

### **Yield**
- Production data with unit conversion
- Crop linkage
- Performance notes

### **DiseaseLog**
- Disease/pest information
- Severity assessment
- Treatment documentation

### **Reminder**
- Task management
- Priority levels
- Completion tracking

### **Note**
- Farmer observations
- Timestamped entries

---

## 🔧 Configuration

Edit `.env` file to customize:

```
FLASK_ENV=production              # Set to production
SECRET_KEY=your_secret_key        # Change this!
OPENWEATHERMAP_API_KEY=your_key   # Optional weather
FARM_LATITUDE=26.1445             # Your farm location
FARM_LONGITUDE=91.7362
DATABASE_URL=sqlite:///farm_data.db
```

---

## 🌐 Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Home page with dashboard |
| `/dashboard` | GET | Financial overview |
| `/add_record` | POST | Add new record |
| `/edit_record/<id>` | GET/POST | Edit record |
| `/delete_record/<id>` | POST | Delete record |
| `/crops` | GET/POST | Manage crops |
| `/edit_crop/<id>` | GET/POST | Edit crop |
| `/delete_crop/<id>` | POST | Delete crop |
| `/yield` | GET/POST | Track yield |
| `/delete_yield/<id>` | POST | Delete yield |
| `/disease_log` | GET/POST | Log diseases |
| `/delete_disease/<id>` | POST | Delete disease |
| `/reminders` | GET/POST | Manage tasks |
| `/complete_reminder/<id>` | POST | Mark complete |
| `/delete_reminder/<id>` | POST | Delete reminder |
| `/calendar` | GET | Monthly calendar |
| `/reports` | GET | Analytics |
| `/notes` | GET/POST | Farmer notes |

---

## 💡 Usage Tips

### Adding Records
1. Go to Dashboard
2. Fill in Activity, Category (Expense/Income), and Expense Type (if expense)
3. Add backdated records by changing the date
4. View and edit past records in the table

### Tracking Crops
1. Go to Crop Management → Add Crop
2. Enter crop details (name, variety, area, season)
3. Link yields and diseases to the crop
4. Monitor crop health in reports

### Monitoring Health
1. Log diseases with severity level
2. Document treatment approach
3. Track affected areas
4. View disease trends in reports

### Task Management
1. Create reminders with due dates
2. Set priority levels
3. Mark tasks complete when done
4. View calendar for at-a-glance status

---

## 📊 Expense Categories

- **🛢️ Fuel** - Diesel, petrol, tractor fuel
- **👷 Labour** - Worker wages, hiring costs
- **🥕 Food/Seeds** - Seeds, fertilizers, pesticides
- **🚚 Transportation** - Vehicle maintenance, shipping
- **📦 Misc** - Other expenses

---

## 🔒 Security Features

- ✅ Secure session management
- ✅ CSRF protection in forms
- ✅ SQLite database with encryption option
- ✅ Environment variable management
- ✅ Production-ready configurations
- ✅ Input validation and sanitization

---

## 📞 Support

For issues or questions:
1. Check DEPLOYMENT_GUIDE.md
2. Review error logs
3. Verify database connectivity
4. Check environment variables

---

## 📝 License

This project is provided as-is for agricultural management.

---

**Version:** 1.0  
**Last Updated:** February 1, 2026  
**Status:** Production Ready ✅
