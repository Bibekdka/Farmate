"""Script to update admin template references for the /admin prefix."""
import os
import re

# Map old route names to new admin_ prefixed names
route_map = {
    'home': 'admin_home',
    'dashboard': 'admin_dashboard',
    'calendar_view': 'admin_calendar_view',
    'weather_history': 'admin_weather_history',
    'daily_log': 'admin_daily_log',
    'save_daily_log': 'admin_save_daily_log',
    'quick_note': 'admin_quick_note',
    'add_record': 'admin_add_record',
    'edit_record': 'admin_edit_record',
    'delete_record': 'admin_delete_record',
    'crops': 'admin_crops',
    'edit_crop': 'admin_edit_crop',
    'delete_crop': 'admin_delete_crop',
    'yield_tracking': 'admin_yield_tracking',
    'delete_yield': 'admin_delete_yield',
    'disease_log': 'admin_disease_log',
    'delete_disease': 'admin_delete_disease',
    'reminders': 'admin_reminders',
    'complete_reminder': 'admin_complete_reminder',
    'delete_reminder': 'admin_delete_reminder',
    'reports': 'admin_reports',
    'knowledge_hub': 'admin_knowledge_hub',
    'notes': 'admin_notes',
    'edit_note': 'admin_edit_note',
    'delete_note': 'admin_delete_note',
    'download_export': 'admin_download_export',
    'financial_data_api': 'admin_financial_data_api',
    'analyze_logs_api': 'admin_analyze_logs_api',
    'ask_crop_doctor': 'admin_ask_crop_doctor',
    'recommend_crops_api': 'admin_recommend_crops_api',
    'diagnose_disease_api': 'admin_diagnose_disease_api',
    'estimate_duration_api': 'admin_estimate_duration_api',
    'backup_status_api': 'admin_backup_status_api',
    'run_manual_backup': 'admin_run_manual_backup',
    'api_check_etl': 'admin_api_check_etl',
    'run_add_historical_weather': 'admin_run_add_historical_weather',
}

admin_dir = 'templates/admin'
for fname in os.listdir(admin_dir):
    if not fname.endswith('.html') or fname == 'base.html':
        continue
    fpath = os.path.join(admin_dir, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace extends
    content = content.replace("{% extends 'base.html' %}", "{% extends 'admin/base.html' %}")

    # Replace url_for references - sort by length descending to avoid partial matches
    sorted_routes = sorted(route_map.items(), key=lambda x: len(x[0]), reverse=True)
    for old_name, new_name in sorted_routes:
        pattern = r"url_for\('" + re.escape(old_name) + r"'"
        replacement = "url_for('" + new_name + "'"
        content = re.sub(pattern, replacement, content)

    # Also replace bare fetch URLs like /api/
    content = content.replace("fetch('/api/", "fetch('/admin/api/")

    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Updated: {fname}')

print('Done!')
