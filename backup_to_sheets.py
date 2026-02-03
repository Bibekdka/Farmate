# Google Sheets Backup Integration
# Requirements: pip install gspread oauth2client

import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path

try:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    SHEETS_AVAILABLE = True
except ImportError:
    SHEETS_AVAILABLE = False
    print("⚠️ Google Sheets libraries not installed")
    print("   Run: pip install gspread oauth2client")

def export_to_google_sheets():
    """Export database to Google Sheets for cloud backup"""
    if not SHEETS_AVAILABLE:
        return False
    
    # Check for credentials
    creds_file = os.environ.get('GOOGLE_SHEETS_CREDENTIALS', 'google_sheets_credentials.json')
    if not Path(creds_file).exists():
        print(f"⚠️ Google Sheets credentials not found: {creds_file}")
        print("   To enable Google Sheets backup:")
        print("   1. Create a Google Cloud project")
        print("   2. Enable Google Sheets API")
        print("   3. Download credentials JSON")
        print("   4. Save as 'google_sheets_credentials.json'")
        return False
    
    try:
        # Authenticate
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
        client = gspread.authorize(creds)
        
        # Open or create spreadsheet
        sheet_name = os.environ.get('GOOGLE_SHEET_NAME', 'FarmApp_Backup')
        try:
            spreadsheet = client.open(sheet_name)
        except gspread.SpreadsheetNotFound:
            spreadsheet = client.create(sheet_name)
            print(f"✅ Created new Google Sheet: {sheet_name}")
        
        # Export each table
        db_path = Path('instance/farm_data.db')
        if not db_path.exists():
            print("⚠️ Database not found")
            return False
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        for table_name in tables:
            try:
                # Get table data
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                
                # Get column names
                column_names = [description[0] for description in cursor.description]
                
                # Create or update worksheet
                try:
                    worksheet = spreadsheet.worksheet(table_name)
                    worksheet.clear()
                except gspread.WorksheetNotFound:
                    worksheet = spreadsheet.add_worksheet(title=table_name, rows=1000, cols=20)
                
                # Write data
                worksheet.update([column_names] + [list(row) for row in rows])
                print(f"✅ Backed up table '{table_name}' ({len(rows)} rows)")
                
            except Exception as e:
                print(f"⚠️ Failed to backup table '{table_name}': {e}")
        
        conn.close()
        
        # Add metadata sheet
        try:
            meta_sheet = spreadsheet.worksheet('_Metadata')
            meta_sheet.clear()
        except gspread.WorksheetNotFound:
            meta_sheet = spreadsheet.add_worksheet(title='_Metadata', rows=100, cols=5)
        
        metadata = [
            ['Backup Timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Database Size (KB)', f"{db_path.stat().st_size / 1024:.2f}"],
            ['Total Tables', str(len(tables))],
            ['Tables Backed Up', ', '.join(tables)]
        ]
        meta_sheet.update(metadata)
        
        print(f"\n✅ Google Sheets backup complete!")
        print(f"   URL: {spreadsheet.url}")
        return True
        
    except Exception as e:
        print(f"❌ Google Sheets backup failed: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("☁️ GOOGLE SHEETS CLOUD BACKUP")
    print("=" * 60)
    export_to_google_sheets()
