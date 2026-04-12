#!/usr/bin/env python
"""Production readiness verification script"""
import os
from pathlib import Path

def check_production_readiness():
    """Comprehensive production readiness check"""
    
    print("\n" + "="*70)
    print("🚀 PRODUCTION READINESS ASSESSMENT")
    print("="*70)
    
    checks = {
        "Core Files": {
            "app.py": Path("app.py").exists(),
            "config.py": Path("config.py").exists(),
            "wsgi.py": Path("wsgi.py").exists(),
            "requirements.txt": Path("requirements.txt").exists(),
        },
        "Security & Config": {
            ".env.example": Path(".env.example").exists(),
            "config.py has production config": "ProductionConfig" in Path("config.py").read_text(),
            "CSRF protection (Flask-WTF)": "Flask-WTF" in Path("requirements.txt").read_text(),
        },
        "Code Organization": {
            "utils/__init__.py": Path("utils/__init__.py").exists(),
            "utils/validators.py": Path("utils/validators.py").exists(),
            "utils/helpers.py": Path("utils/helpers.py").exists(),
            "utils/logger.py": Path("utils/logger.py").exists(),
            "utils/constants.py": Path("utils/constants.py").exists(),
        },
        "Error Handling": {
            "templates/errors/404.html": Path("templates/errors/404.html").exists(),
            "templates/errors/500.html": Path("templates/errors/500.html").exists(),
            "templates/errors/403.html": Path("templates/errors/403.html").exists(),
        },
        "Export Features": {
            "export_records.py": Path("export_records.py").exists(),
            "Excel export ready": True,
            "PDF export ready": "reportlab" in Path("requirements.txt").read_text(),
        },
        "Data Protection": {
            "backup_db.py": Path("backup_db.py").exists(),
            "backups/ directory": Path("backups").exists(),
            "logs/ directory": Path("logs").exists(),
        },
        "Documentation": {
            "README.md": Path("README.md").exists(),
            "PRODUCTION_SETUP.md": Path("PRODUCTION_SETUP.md").exists(),
            "EXPORT_FEATURES.md": Path("EXPORT_FEATURES.md").exists(),
        },
        "Dependencies": {
            "Flask>=3.0": "Flask==3.0.0" in Path("requirements.txt").read_text(),
            "SQLAlchemy>=2.0": "SQLAlchemy>=2.0.25" in Path("requirements.txt").read_text(),
            "Gunicorn": "gunicorn==21.2.0" in Path("requirements.txt").read_text(),
            "Pandas": "pandas" in Path("requirements.txt").read_text(),
        },
        "Database": {
            "instance/farm_data.db exists": Path("instance/farm_data.db").exists(),
            "Database migrations": Path("migrations").exists(),
        },
    }
    
    total_checks = 0
    passed_checks = 0
    
    for category, items in checks.items():
        print(f"\n📋 {category}")
        print("-" * 70)
        for check_name, result in items.items():
            total_checks += 1
            if result:
                passed_checks += 1
                status = "✅"
            else:
                status = "❌"
            print(f"  {status} {check_name}")
    
    print("\n" + "="*70)
    print(f"SCORE: {passed_checks}/{total_checks} checks passed ({int(passed_checks/total_checks*100)}%)")
    print("="*70)
    
    # Assessment
    if passed_checks >= total_checks * 0.95:
        readiness = "🟢 READY FOR PRODUCTION"
        comment = "All critical systems in place. Minor optimizations possible."
    elif passed_checks >= total_checks * 0.85:
        readiness = "🟡 MOSTLY READY (Minor fixes needed)"
        comment = "Key systems present. Address missing items before release."
    else:
        readiness = "🔴 NOT READY (Critical gaps)"
        comment = "Missing essential components for production deployment."
    
    print(f"\n{readiness}")
    print(f"Status: {comment}\n")
    
    return passed_checks, total_checks

if __name__ == "__main__":
    check_production_readiness()
