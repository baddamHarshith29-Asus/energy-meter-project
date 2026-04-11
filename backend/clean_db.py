from app import create_app
from database import db
from models import UsageData
from datetime import datetime

app = create_app()
with app.app_context():
    # Find records with invalid years
    invalid_records = UsageData.query.filter(UsageData.timestamp > datetime(2260, 1, 1)).all()
    print(f"Found {len(invalid_records)} invalid records.")
    for r in invalid_records:
        print(f"Deleting record with date: {r.timestamp}")
        db.session.delete(r)
    db.session.commit()
    print("Database cleaned.")
