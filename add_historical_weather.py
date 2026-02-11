import os
import datetime
import requests
from dotenv import load_dotenv
from app import app, db, WeatherLog

load_dotenv()

LAT = os.environ.get('FARM_LATITUDE', '26.1445')
LON = os.environ.get('FARM_LONGITUDE', '91.7362')

def get_historical_weather(date_str):
    """Fetch historical weather data from Open-Meteo API"""
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": LAT,
            "longitude": LON,
            "start_date": date_str,
            "end_date": date_str,
            "daily": ["weather_code", "temperature_2m_max", "precipitation_sum"],
            "timezone": "auto"
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        wmo_codes = {
            0: "☀️ Clear Sky",
            1: "🌤️ Mainly Clear", 2: "⛅ Partly Cloudy", 3: "☁️ Overcast",
            45: "🌫️ Fog", 48: "🌫️ Rime Fog",
            51: "DRIZZLE: Light", 53: "DRIZZLE: Moderate", 55: "DRIZZLE: Dense",
            61: "Rain: Slight", 63: "RAINING: Moderate", 65: "RAINING: Heavy",
            71: "SNOW: Slight", 73: "SNOW: Moderate", 75: "SNOW: Heavy",
            80: "SHOWERS: Slight", 81: "SHOWERS: Moderate", 82: "SHOWERS: Violent",
            95: "⚡ Thunderstorm", 96: "⚡ Thunderstorm + Hail", 99: "⚡ Thunderstorm + Heavy Hail"
        }
        
        if response.status_code == 200 and 'daily' in data:
            daily = data['daily']
            code = daily['weather_code'][0]
            desc = wmo_codes.get(code, f"Code: {code}")
            
            return {
                'temp': daily['temperature_2m_max'][0],
                'rainfall': daily['precipitation_sum'][0],
                'desc': desc
            }
    except Exception as e:
        print(f"Error fetching weather for {date_str}: {e}")
    return None

# Check for missing dates in the last 60 days
with app.app_context():
    print("Checking for missing weather data in the last 60 days...")
    
    today = datetime.date.today()
    start_check_date = today - datetime.timedelta(days=60)
    
    # Get all existing dates
    existing_logs = WeatherLog.query.filter(WeatherLog.date >= start_check_date).all()
    existing_dates = {log.date for log in existing_logs}
    
    # Identify missing dates
    missing_dates = []
    current = start_check_date
    while current < today:
        if current not in existing_dates:
            missing_dates.append(current)
        current += datetime.timedelta(days=1)
    
    if not missing_dates:
        print("[OK] No missing dates found in the last 60 days.")
    else:
        print(f"Found {len(missing_dates)} missing days. Starting import...")
        count = 0
        for date in missing_dates:
            try:
                weather_data = get_historical_weather(date.strftime('%Y-%m-%d'))
                if weather_data:
                    new_log = WeatherLog(
                        date=date,
                        max_temp=weather_data['temp'],
                        rainfall=weather_data['rainfall'],
                        description=weather_data['desc'],
                        created_at=datetime.datetime.now()
                    )
                    db.session.add(new_log)
                    print(f"[ADDED] {date}: {weather_data['temp']}C, {weather_data['desc']}")
                    count += 1
                else:
                    print(f"[FAIL] Could not fetch data for {date}")
            except Exception as e:
                print(f"[ERROR] {date}: {e}")
        
        db.session.commit()
        print(f"\n[DONE] Successfully added {count} missing weather records.")

