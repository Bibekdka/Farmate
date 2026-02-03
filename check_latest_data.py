import os
import shutil
from pathlib import Path
from datetime import datetime

def find_latest_backup():
    """Find the most recent backup file from all backup locations"""
    backup_locations = [
        Path('backups'),
        Path(os.environ.get('USERPROFILE', '')) / 'OneDrive' / 'FarmApp_Backups',
        Path(os.environ.get('USERPROFILE', '')) / 'Desktop' / 'FarmApp_Emergency_Backups'
    ]
    
    all_backups = []
    
    for location in backup_locations:
        if location.exists():
            for backup in location.rglob('*.db'):
                if backup.is_file():
                    all_backups.append({
                        'path': backup,
                        'modified': backup.stat().st_mtime,
                        'modified_dt': datetime.fromtimestamp(backup.stat().st_mtime),
                        'size': backup.stat().st_size
                    })
    
    if not all_backups:
        return None
    
    # Sort by modification time, newest first
    all_backups.sort(key=lambda x: x['modified'], reverse=True)
    return all_backups[0]

def restore_latest_backup():
    """Restore the latest backup if it's newer than current database"""
    db_path = Path('instance/farm_data.db')
    
    # Find latest backup
    latest_backup = find_latest_backup()
    
    if not latest_backup:
        print("No backups found.")
        return False
    
    # Check if current DB exists
    if not db_path.exists():
        print(f"No database found. Restoring from backup: {latest_backup['path']}")
        db_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(latest_backup['path'], db_path)
        print(f"✅ Database restored from {latest_backup['modified_dt']}")
        return True
    
    # Compare timestamps
    current_db_time = db_path.stat().st_mtime
    backup_time = latest_backup['modified']
    
    if backup_time > current_db_time:
        print(f"⚠️ Backup is newer than current database!")
        print(f"   Current DB: {datetime.fromtimestamp(current_db_time)}")
        print(f"   Backup: {latest_backup['modified_dt']}")
        print(f"   Restoring latest backup...")
        
        # Backup current before replacing
        current_backup = db_path.parent / f"before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(db_path, current_backup)
        print(f"   Saved current DB as: {current_backup}")
        
        # Restore latest backup
        shutil.copy2(latest_backup['path'], db_path)
        print(f"✅ Database restored to latest version from {latest_backup['modified_dt']}")
        return True
    else:
        print(f"✅ Current database is up to date ({datetime.fromtimestamp(current_db_time)})")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("🔍 CHECKING FOR LATEST DATABASE VERSION")
    print("=" * 60)
    restore_latest_backup()
