# Constants and configuration
import os

# Weather API
WMO_CODES = {
    0: "☀️ Clear Sky",
    1: "🌤️ Mainly Clear", 2: "⛅ Partly Cloudy", 3: "☁️ Overcast",
    45: "🌫️ Fog", 48: "🌫️ Rime Fog",
    51: "DRIZZLE: Light", 53: "DRIZZLE: Moderate", 55: "DRIZZLE: Dense",
    61: "Rain: Slight", 63: "RAINING: Moderate", 65: "RAINING: Heavy",
    71: "SNOW: Slight", 73: "SNOW: Moderate", 75: "SNOW: Heavy",
    77: "❄️ Snow Grains",
    80: "SHOWERS: Slight", 81: "SHOWERS: Moderate", 82: "SHOWERS: Violent",
    95: "⚡ Thunderstorm", 96: "⚡ Thunderstorm + Hail", 99: "⚡ Thunderstorm + Heavy Hail"
}

# Yield conversions
YIELD_CONVERSIONS = {'kg': 1, 'quintal': 100, 'tons': 1000, 'grams': 0.001}

# Expense types
EXPENSE_TYPES = ['Fuel', 'Labour', 'Seed', 'Water', 'Transportation', 'Medicine', 'Misc']

# Farm location (load from env)
FARM_LATITUDE = float(os.environ.get('FARM_LATITUDE', '26.1445'))
FARM_LONGITUDE = float(os.environ.get('FARM_LONGITUDE', '91.7362'))

# Pagination
RECORDS_PER_PAGE = 50

# Data files
DATA_FILES = {
    'pest_etl': 'data/pest_etl.json',
    'pest_calendar': 'data/pest_calendar.json',
    'crop_calendar': 'data/crop_calendar.json',
    'turmeric_data': 'data/turmeric_data.json',
}

# Alert thresholds
PEST_ALERT_WEATHER_TEMP_THRESHOLD = 25
PEST_ALERT_WEATHER_HUMIDITY_THRESHOLD = 80
