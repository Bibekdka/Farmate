import os
import datetime
import pandas as pd

from app import app, db, FarmRecord, WeatherLog


def export_records(output_dir='exports'):
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    out_path = os.path.join(output_dir, f'records_export_{timestamp}.xlsx')

    with app.app_context():
        # Expenses only
        expenses_q = FarmRecord.query.filter(FarmRecord.category == 'Expense').order_by(FarmRecord.date.asc()).all()
        expenses = [
            {
                'id': r.id,
                'date': r.date.isoformat() if r.date else None,
                'activity_type': r.activity_type,
                'expense_type': r.expense_type,
                'amount': r.amount,
                'description': r.description
            }
            for r in expenses_q
        ]

        # All farm records
        all_q = FarmRecord.query.order_by(FarmRecord.date.asc()).all()
        all_records = [
            {
                'id': r.id,
                'date': r.date.isoformat() if r.date else None,
                'activity_type': r.activity_type,
                'category': r.category,
                'expense_type': r.expense_type,
                'amount': r.amount,
                'description': r.description
            }
            for r in all_q
        ]

        # Weather logs
        weather_q = WeatherLog.query.order_by(WeatherLog.date.asc()).all()
        weather = [
            {
                'id': w.id,
                'date': w.date.isoformat() if w.date else None,
                'max_temp': w.max_temp,
                'rainfall': w.rainfall,
                'description': w.description
            }
            for w in weather_q
        ]

    # Create DataFrames
    writer = pd.ExcelWriter(out_path, engine='openpyxl')

    if all_records:
        pd.DataFrame(all_records).to_excel(writer, sheet_name='all_records', index=False)
    else:
        pd.DataFrame([], columns=['id','date','activity_type','category','expense_type','amount','description']).to_excel(writer, sheet_name='all_records', index=False)

    if expenses:
        pd.DataFrame(expenses).to_excel(writer, sheet_name='expenses', index=False)
    else:
        pd.DataFrame([], columns=['id','date','activity_type','expense_type','amount','description']).to_excel(writer, sheet_name='expenses', index=False)

    if weather:
        pd.DataFrame(weather).to_excel(writer, sheet_name='weather', index=False)
    else:
        pd.DataFrame([], columns=['id','date','max_temp','rainfall','description']).to_excel(writer, sheet_name='weather', index=False)

    writer.close()
    return out_path


if __name__ == '__main__':
    path = export_records()
    print(f'Export written to: {path}')
