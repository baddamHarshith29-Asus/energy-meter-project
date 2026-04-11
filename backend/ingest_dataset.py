from app import create_app
from database import db
from models import BusinessProfile, SimulationScenario
import pandas as pd
import os

app = create_app()

def ingest_data():
    dataset_path = 'c:/Users/chedu/OneDrive/Desktop/energy/backend/data/evaluated_scenarios.xlsx'
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset not found at {dataset_path}")
        return

    df = pd.read_excel(dataset_path)
    
    with app.app_context():
        print("Starting evaluated scenario ingestion...")
        # Clear existing tables (since we altered schema)
        db.drop_all()
        db.create_all()

        profiles_count = 0
        scenarios_count = 0
        
        for _, row in df.iterrows():
            try:
                # Create profile
                profile = BusinessProfile(
                    business_name=row['business_name'],
                    industry=row['industry'],
                    employees=row['employees'],
                    working_days=row['working_days'],
                    working_hours=row['working_hours'],
                    machines=row['machines'],
                    machine_runtime=row['machine_runtime'],
                    monthly_units=row['monthly_units'],
                    cost_per_unit=row['cost_per_unit']
                )
                db.session.add(profile)
                db.session.flush() # Get ID
                profiles_count += 1
                
                # Insert the fully evaluated AI-powered configuration scenario
                scenario = SimulationScenario(
                    business_profile_id=profile.id,
                    scenario_name=f"Automated AI Optimization -> {row['scenario_reduce_runtime_pct']}% Load Drop",
                    reduce_runtime_pct=float(row['scenario_reduce_runtime_pct']),
                    reduce_hours=float(row['scenario_reduce_hours']),
                    projected_savings=float(row['projected_savings']), 
                    efficiency_score=float(row['efficiency_score']),
                    ai_explanation=str(row['ai_explanation'])
                )
                db.session.add(scenario)
                scenarios_count += 1
                
            except Exception as e:
                print(f"Skipping row due to error: {e}")
                continue
        
        db.session.commit()
        print(f"Successfully ingested {profiles_count} Profiles and {scenarios_count} AI-Evaluated Scenarios.")

if __name__ == '__main__':
    ingest_data()
