# Helper functions for business logic
import json
import logging
from pathlib import Path
from utils.constants import YIELD_CONVERSIONS, DATA_FILES

logger = logging.getLogger(__name__)


def convert_to_kg(value, unit):
    """Convert yield value to kilograms."""
    try:
        return float(value) * YIELD_CONVERSIONS.get(unit.lower(), 1)
    except (ValueError, TypeError):
        logger.warning(f"Invalid yield conversion: value={value}, unit={unit}")
        return 0.0


def load_json_file(file_key):
    """Safely load JSON data files."""
    try:
        file_path = DATA_FILES.get(file_key)
        if not file_path or not Path(file_path).exists():
            logger.warning(f"Data file not found: {file_path}")
            return {} if file_key == 'pest_etl' else []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {file_key}: {e}")
        return {} if file_key == 'pest_etl' else []


def load_all_knowledge_bases():
    """Load all knowledge base files."""
    return {
        'pest_etl': load_json_file('pest_etl'),
        'pest_calendar': load_json_file('pest_calendar'),
        'crop_calendar': load_json_file('crop_calendar'),
        'turmeric_data': load_json_file('turmeric_data'),
    }


def format_date_display(date_obj):
    """Format date for display."""
    if not date_obj:
        return "-"
    return date_obj.strftime('%A, %d %B %Y')


def calculate_days_remaining(harvest_date):
    """Calculate days remaining until harvest."""
    from datetime import date
    if not harvest_date:
        return None
    days = (harvest_date - date.today()).days
    return days if days >= 0 else None
