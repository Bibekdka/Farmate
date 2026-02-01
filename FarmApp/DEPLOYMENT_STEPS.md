# 🚀 PRODUCTION DEPLOYMENT - STEP BY STEP GUIDE

## 📦 PROJECT IS PRODUCTION READY ✅

Your Smart Farmer application is fully cleaned up and ready for production deployment.

---

## 📁 PROJECT STRUCTURE (FINAL)

```
c:\Users\abhij\OneDrive\Desktop\Agriculture\FarmApp\
├── 📄 app.py                    # Main Flask application
├── 📄 config.py                 # Configuration management (dev/prod)
├── 📄 wsgi.py                   # Production WSGI entry point
├── 📄 requirements.txt           # Python dependencies
├── 📄 .env.example              # Environment variables template
├── 📄 .gitignore                # Git ignore patterns
├── 📄 README.md                 # Project documentation
├── 📄 DEPLOYMENT_GUIDE.md       # Detailed deployment instructions
├── 📄 DEPLOYMENT_CHECKLIST.txt  # Checklist
│
├── 📁 templates/                # 12 HTML templates
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   ├── calendar.html
│   ├── crops.html
│   ├── edit_crop.html
│   ├── yield.html
│   ├── disease_log.html
│   ├── reminders.html
│   ├── reports.html
│   ├── edit_record.html
│   └── notes.html
│
└── 📁 instance/
    └── farm_data.db             # SQLite database
```

---

## ✅ CLEANUP COMPLETED

Removed files:
- ❌ `test_features.py` (testing file)
- ❌ `FEATURES_GUIDE.md` (documentation)
- ❌ `for context/` (context folder)
- ❌ Old development files

---

## 🎯 PRODUCTION DEPLOYMENT PATHS

### **PATH 1: Windows Server with IIS** (30 mins)

**1. Prerequisites:**
```powershell
# Install Python 3.10+ from https://www.python.org/downloads/
# Download FastCGI: https://www.iis.net/downloads/recommended/url-rewrite-module
```

**2. Setup Project:**
```powershell
# Create project folder
mkdir C:\SmartFarmer
cd C:\SmartFarmer

# Copy FarmApp files here
# Copy-Item C:\...\FarmApp\* -Destination C:\SmartFarmer -Recurse

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt
```

**3. Configure:**
```powershell
# Create .env file
copy .env.example .env

# Edit .env with actual values
notepad .env
```

**4. IIS Setup:**
- Open IIS Manager
- Create new website: `C:\SmartFarmer`
- Install FastCGI module
- Create web.config (see DEPLOYMENT_GUIDE.md)

**5. Verify:**
```
http://your-server-ip
```

---

### **PATH 2: Linux Server with Nginx + Gunicorn** (45 mins) 🔥 RECOMMENDED

**1. SSH to Server:**
```bash
ssh user@your-server-ip
```

**2. Install Dependencies:**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv nginx -y
```

**3. Setup Project:**
```bash
sudo mkdir -p /var/www/smartfarmer
cd /var/www/smartfarmer

# Copy FarmApp files
sudo cp -r /path/to/FarmApp/* .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**4. Create Environment:**
```bash
cp .env.example .env
sudo nano .env
# Edit with real values (SECRET_KEY, API keys, etc.)
```

**5. Create Systemd Service:**
```bash
sudo tee /etc/systemd/system/smartfarmer.service > /dev/null <<EOF
[Unit]
Description=Smart Farmer Flask App
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/smartfarmer
Environment="PATH=/var/www/smartfarmer/venv/bin"
ExecStart=/var/www/smartfarmer/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl start smartfarmer
sudo systemctl enable smartfarmer
```

**6. Configure Nginx:**
```bash
sudo tee /etc/nginx/sites-available/smartfarmer > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/smartfarmer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

**7. Add SSL (Free):**
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

**8. Verify:**
```
https://your-domain.com
```

**Status Command:**
```bash
sudo systemctl status smartfarmer
sudo journalctl -u smartfarmer -f  # View logs
```

---

### **PATH 3: Heroku** (15 mins) ⚡ EASIEST

**1. Install Heroku CLI:**
```bash
# Download from https://devcenter.heroku.com/articles/heroku-cli
```

**2. Login:**
```bash
heroku login
```

**3. Create App:**
```bash
cd C:\path\to\FarmApp
heroku create your-app-name
```

**4. Configure Environment:**
```bash
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-very-secure-key
heroku config:set OPENWEATHERMAP_API_KEY=your_key
```

**5. Deploy:**
```bash
git push heroku main
```

**6. Monitor:**
```bash
heroku logs --tail
heroku open
```

---

### **PATH 4: PythonAnywhere** (20 mins) 📝 NO CODING

**1. Visit:** https://www.pythonanywhere.com/

**2. Create Free Account**

**3. Upload Files:**
- Use file manager to upload FarmApp contents

**4. Configure Web App:**
- Source code: /home/username/mysite/FarmApp
- WSGI file: wsgi.py

**5. Set Variables:**
- Paste .env contents into environment variables

**6. Reload Web App**

**7. Visit:**
```
https://username.pythonanywhere.com
```

---

## ⚙️ ENVIRONMENT VARIABLES (.env)

**Required:**
```
FLASK_ENV=production
SECRET_KEY=<generate-random-32-char-key>
```

**Optional:**
```
OPENWEATHERMAP_API_KEY=your_api_key_from_openweather
FARM_LATITUDE=26.1445
FARM_LONGITUDE=91.7362
DATABASE_URL=sqlite:///farm_data.db
```

**Generate Secure Key (Python):**
```python
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🔒 SECURITY CHECKLIST

Before going LIVE:

- [ ] **Change SECRET_KEY** (unique for each deployment)
- [ ] **Set FLASK_ENV=production** (not development)
- [ ] **Enable HTTPS/SSL** (free on Let's Encrypt)
- [ ] **Disable Debug Mode** (automatically in production)
- [ ] **Set Strong Passwords** (database, admin access)
- [ ] **Configure Firewall** (allow only ports 80, 443)
- [ ] **Enable Database Backups** (daily automatic)
- [ ] **Add Monitoring** (uptime checks, error logs)
- [ ] **Update Dependencies** (run: `pip install -r requirements.txt --upgrade`)
- [ ] **Test Functionality** (go through all features once)

---

## 📊 POST-DEPLOYMENT

### Monitor Application:
```bash
# Linux
sudo systemctl status smartfarmer
sudo journalctl -u smartfarmer -n 100

# Windows (IIS)
# Check Event Viewer
```

### Backup Database:
```bash
# Linux
sudo cp /var/www/smartfarmer/instance/farm_data.db /backup/farm_data_$(date +%Y-%m-%d).db

# Windows
copy "C:\SmartFarmer\instance\farm_data.db" "C:\Backup\farm_data_%date:~0,10%.db"
```

### Update Application:
```bash
# Stop service
sudo systemctl stop smartfarmer

# Pull latest code
cd /var/www/smartfarmer
git pull origin main

# Install any new dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Restart
sudo systemctl start smartfarmer
```

---

## 🆘 TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| **Port in use** | Kill process: `lsof -i :8000` then `kill -9 <PID>` |
| **Database locked** | Stop app, delete farm_data.db, restart |
| **500 error** | Check logs: `journalctl -u smartfarmer` |
| **Templates not found** | Verify templates/ folder exists and has permissions |
| **Static files missing** | Ensure templates/ folder is readable by web server |
| **Weather API error** | Add real OpenWeatherMap API key or leave blank |

---

## 📞 QUICK COMMAND REFERENCE

### Development Testing:
```bash
python app.py
# Visit: http://localhost:5000
```

### Production (Linux):
```bash
gunicorn --workers 4 --bind 0.0.0.0:8000 wsgi:app
```

### Database:
```bash
# Initialize
python app.py  # Runs once, creates farm_data.db

# Backup
cp instance/farm_data.db instance/farm_data_backup.db
```

### View Logs:
```bash
# Linux
tail -f /var/log/smartfarmer.log
journalctl -u smartfarmer -f

# Windows
# Event Viewer → Application
```

---

## 📋 FINAL CHECKLIST

### Before Deployment:
- [ ] All unwanted files removed
- [ ] requirements.txt includes all dependencies
- [ ] .env.example provided as template
- [ ] config.py sets up dev/prod configs
- [ ] wsgi.py file created for production
- [ ] README.md documentation complete
- [ ] DEPLOYMENT_GUIDE.md provided
- [ ] App tested on localhost
- [ ] Database initialized and tested

### During Deployment:
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] .env file created from template
- [ ] Environment variables set
- [ ] Web server configured
- [ ] SSL/HTTPS enabled
- [ ] Firewall configured
- [ ] Backup system set up

### After Deployment:
- [ ] App loads without errors
- [ ] All features tested
- [ ] Database backups working
- [ ] Monitoring configured
- [ ] Team trained on deployment
- [ ] Documentation shared

---

## 🎓 ADDITIONAL RESOURCES

- **Flask Docs:** https://flask.palletsprojects.com/
- **SQLAlchemy:** https://docs.sqlalchemy.org/
- **Gunicorn:** https://docs.gunicorn.org/
- **Nginx:** https://nginx.org/en/docs/
- **Let's Encrypt SSL:** https://letsencrypt.org/

---

**Status:** ✅ PRODUCTION READY  
**Version:** 1.0  
**Last Updated:** February 1, 2026

Choose your deployment path above and follow the steps. 

**Questions?** Refer to DEPLOYMENT_GUIDE.md for detailed instructions.
