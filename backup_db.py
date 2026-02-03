import os
import shutil
import datetime
from pathlib import Path

# Automatic Database Backup Script
def create_backup():
    """Create a timestamped backup of the database"""
    db_path = Path('instance/farm_data.db')
    
    if not db_path.exists():
        print("⚠️ No database file found to backup")
        return
    
    # Create backups directory if it doesn't exist
    backup_dir = Path('backups')
    backup_dir.mkdir(exist_ok=True)
    
    # Create timestamped backup
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = backup_dir / f'farm_data_backup_{timestamp}.db'
    
    # Copy database
    shutil.copy2(db_path, backup_path)
    
    print(f"✅ Database backed up to: {backup_path}")
    print(f"   Size: {backup_path.stat().st_size / 1024:.2f} KB")
    
    # Keep only last 10 backups
    backups = sorted(backup_dir.glob('farm_data_backup_*.db'), key=lambda x: x.stat().st_mtime, reverse=True)
    if len(backups) > 10:
        for old_backup in backups[10:]:
            old_backup.unlink()
            print(f"🗑️ Removed old backup: {old_backup.name}")

if __name__ == '__main__':
    create_backup()
