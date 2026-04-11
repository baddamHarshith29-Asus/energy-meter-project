from app import create_app, db
from models import Branch, UsageData
from datetime import datetime, timedelta
import random

app = create_app()

def seed_data():
    with app.app_context():
        # Create branches
        b1 = Branch(name="Main Office", location="New York")
        b2 = Branch(name="Factory A", location="Chicago")
        db.session.add(b1)
        db.session.add(b2)
        db.session.commit()
        
        # Add usage data for the last 6 months
        start_date = datetime.now() - timedelta(days=180)
        
        for i in range(180):
            date = start_date + timedelta(days=i)
            
            # Main Office usage (relatively stable)
            u1 = UsageData(
                branch_id=b1.id,
                timestamp=date,
                units_kwh=random.uniform(50, 80),
                cost=random.uniform(10, 20),
                peak_usage=date.hour > 17
            )
            
            # Factory A usage (higher and more variable)
            u2 = UsageData(
                branch_id=b2.id,
                timestamp=date,
                units_kwh=random.uniform(200, 500),
                cost=random.uniform(50, 150),
                peak_usage=date.hour > 8 and date.hour < 18
            )
            
            db.session.add(u1)
            db.session.add(u2)
            
        # Add some anomalies
        a1 = UsageData(
            branch_id=b1.id,
            timestamp=datetime.now() - timedelta(days=5),
            units_kwh=150, # Spike
            cost=40,
            is_anomaly=True,
            explanation="Unusual spike detected in the evening."
        )
        db.session.add(a1)
        
        db.session.commit()
        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_data()
