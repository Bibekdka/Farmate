# 🌾 Smart Farmer App - Production Deployment Guide

## Project Structure (Production Ready)
```
FarmApp/
├── app.py                    # Main Flask application
├── config.py                 # Configuration management
├── wsgi.py                   # WSGI entry point for production servers
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore file
├── templates/                # HTML templates
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
├── instance/
│   └── farm_data.db          # SQLite database (auto-created)
└── README.md                 # This file
```

---

## 🚀 DEPLOYMENT STEPS

### **Step 1: Prepare Your Server**

#### For Windows Server:
```powershell
# Install Python 3.10+ if not already installed
# Download from: https://www.python.org/downloads/

# Create a project directory
mkdir C:\SmartFarmer
cd C:\SmartFarmer

# Copy all FarmApp files here
```

#### For Linux/Ubuntu Server:
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Create project directory
sudo mkdir -p /var/www/smartfarmer
cd /var/www/smartfarmer
```

---

### **Step 2: Set Up Python Virtual Environment**

#### Windows:
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt
```

#### Linux/Ubuntu:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### **Step 3: Configure Environment Variables**

1. **Create `.env` file** in the FarmApp directory:

```bash
# Copy the template
cp .env.example .env
```

2. **Edit `.env` file with production settings:**

```
FLASK_ENV=production
FLASK_APP=app.py
SECRET_KEY=your_very_secure_random_key_here_min_32_chars
OPENWEATHERMAP_API_KEY=your_actual_api_key_from_openweather
FARM_LATITUDE=26.1445
FARM_LONGITUDE=91.7362
DATABASE_URL=sqlite:///farm_data.db
```

**To generate a secure SECRET_KEY (Python):**
```python
import secrets
print(secrets.token_hex(32))
```

---

### **Step 4: Initialize Database**

```bash
# Activate venv first
# Windows: .\venv\Scripts\Activate
# Linux: source venv/bin/activate

# Initialize database
python app.py

# The database will be created automatically in instance/farm_data.db
```

---

### **Step 5: Test Local Deployment**

```bash
# Start the Flask development server (for testing only)
python app.py

# Open browser and visit: http://localhost:5000
# Test all features before production deployment
```

---

## 🌐 PRODUCTION SERVER SETUP

### **Option A: Deploy on Windows Server with IIS**

1. **Install IIS with CGI Support:**
   - Open Server Manager → Add Roles and Features
   - Select Web Server (IIS) → CGI
   - Install FastCGI Module

2. **Install wfastcgi:**
```powershell
pip install wfastcgi
wfastcgi-enable
```

3. **Create IIS Application:**
   - Open IIS Manager
   - Add new website pointing to `C:\SmartFarmer\FarmApp`
   - Set Application Pool to Python

4. **Add web.config:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="FastCGI" path="*" verb="*" modules="FastCgiModule" scriptProcessor="C:\SmartFarmer\venv\Scripts\wfastcgi.py|app" resourceType="Unspecified" requireAccess="Script" />
    </handlers>
  </system.webServer>
</configuration>
```

---

### **Option B: Deploy on Linux with Gunicorn + Nginx**

#### 1. **Install Nginx:**
```bash
sudo apt install nginx -y
sudo systemctl start nginx
sudo systemctl enable nginx
```

#### 2. **Create Nginx Configuration:**
```bash
sudo nano /etc/nginx/sites-available/smartfarmer
```

```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 3. **Enable Nginx Site:**
```bash
sudo ln -s /etc/nginx/sites-available/smartfarmer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 4. **Create Systemd Service:**
```bash
sudo nano /etc/systemd/system/smartfarmer.service
```

```ini
[Unit]
Description=Smart Farmer Flask App
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/smartfarmer
Environment="PATH=/var/www/smartfarmer/venv/bin"
ExecStart=/var/www/smartfarmer/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 wsgi:app

[Install]
WantedBy=multi-user.target
```

#### 5. **Start Service:**
```bash
sudo systemctl daemon-reload
sudo systemctl start smartfarmer
sudo systemctl enable smartfarmer
sudo systemctl status smartfarmer
```

---

### **Option C: Deploy on Heroku**

#### 1. **Create Procfile:**
```
web: gunicorn wsgi:app
```

#### 2. **Create runtime.txt:**
```
python-3.11.7
```

#### 3. **Deploy:**
```bash
heroku login
heroku create your-app-name
git push heroku main

# Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your_secret_key
```

---

### **Option D: Deploy on PythonAnywhere**

1. Go to [PythonAnywhere.com](https://www.pythonanywhere.com/)
2. Create free account
3. Upload FarmApp files
4. Configure Web App settings
5. Point to `wsgi.py`
6. Set environment variables in `.env`

---

## 📊 MAINTENANCE & MONITORING

### **Backup Database**

#### Windows:
```powershell
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
Copy-Item -Path "FarmApp\instance\farm_data.db" -Destination "backups\farm_data_$timestamp.db"
```

#### Linux:
```bash
timestamp=$(date +%Y-%m-%d_%H-%M-%S)
cp /var/www/smartfarmer/instance/farm_data.db /backups/farm_data_$timestamp.db
```

### **Monitor Logs**

#### Windows (IIS):
```
C:\inetpub\logs\LogFiles\
```

#### Linux (Systemd):
```bash
sudo journalctl -u smartfarmer -f
```

### **Update Application**

```bash
# Stop application
# Linux: sudo systemctl stop smartfarmer
# Windows: Stop IIS Application Pool

# Pull latest code
git pull origin main

# Install new dependencies if any
pip install -r requirements.txt

# Restart application
# Linux: sudo systemctl start smartfarmer
# Windows: Start IIS Application Pool
```

---

## 🔒 SECURITY CHECKLIST

✅ **Before Going Live:**
- [ ] Change `SECRET_KEY` to a secure random value
- [ ] Set `FLASK_ENV=production` (not development)
- [ ] Use HTTPS/SSL certificate
- [ ] Enable database backups
- [ ] Set up firewall rules
- [ ] Disable debug mode in production
- [ ] Add real OpenWeatherMap API key (optional)
- [ ] Set strong session timeout
- [ ] Use environment variables for secrets (never commit `.env`)
- [ ] Set up regular database maintenance

---

## 🛠️ TROUBLESHOOTING

### **Application won't start:**
```bash
# Check Python version
python --version

# Check dependencies
pip list

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check database permissions
ls -la instance/
```

### **Port already in use:**
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux
sudo lsof -i :8000
sudo kill -9 <PID>
```

### **Database locked error:**
```bash
# Stop application, remove farm_data.db, restart
rm instance/farm_data.db
python app.py
```

### **Static files not loading:**
```bash
# Make sure templates/ directory exists
# Make sure Flask can read the files
ls -la templates/
```

---

## 📞 SUPPORT & DOCUMENTATION

- **Flask Docs:** https://flask.palletsprojects.com/
- **SQLAlchemy Docs:** https://docs.sqlalchemy.org/
- **Gunicorn Docs:** https://docs.gunicorn.org/
- **Nginx Docs:** https://nginx.org/en/docs/

---

## 📈 Performance Tips

1. **Enable caching headers** in Nginx
2. **Use CDN** for static assets
3. **Monitor database size** regularly
4. **Archive old records** periodically
5. **Use connection pooling** for database
6. **Enable gzip compression** in Nginx
7. **Use load balancer** for high traffic

---

**Last Updated:** February 1, 2026  
**Version:** 1.0 Production Ready
