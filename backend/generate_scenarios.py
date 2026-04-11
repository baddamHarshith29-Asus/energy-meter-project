import pandas as pd
import random
import os

def generate_scenario_dataset(output_path, num_records=100):
    industries = ["Manufacturing", "Tech Office", "Textile Mill", "Data Center", "Automotive"]
    data = []
    
    for i in range(num_records):
        industry = random.choice(industries)
        business_name = f"{industry} Corp {i+1}"
        
        # Base configurations depending on industry
        if industry == "Manufacturing" or industry == "Automotive" or industry == "Textile Mill":
            employees = random.randint(50, 500)
            machines = random.randint(10, 50)
            runtime = random.randint(12, 24)
            monthly_units = random.randint(10000, 50000)
        else:
            employees = random.randint(10, 200)
            machines = random.randint(2, 10) # Servers/HVAC units
            runtime = 24
            monthly_units = random.randint(2000, 15000)
            
        working_days = random.randint(20, 26)
        working_hours = random.randint(8, 16)
        cost_per_unit = round(random.uniform(0.10, 0.25), 2)
        
        # Test scenarios
        reduce_runtime = random.randint(5, 30) # % reduction
        reduce_hours = random.randint(1, 4) # absolute hours
        
        data.append({
            "business_name": business_name,
            "industry": industry,
            "employees": employees,
            "working_days": working_days,
            "working_hours": working_hours,
            "machines": machines,
            "machine_runtime": runtime,
            "monthly_units": monthly_units,
            "cost_per_unit": cost_per_unit,
            "scenario_reduce_runtime_pct": reduce_runtime,
            "scenario_reduce_hours": reduce_hours
        })
        
    df = pd.DataFrame(data)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_excel(output_path, index=False)
    print(f"Generated {num_records} simulation scenarios at {output_path}")

if __name__ == "__main__":
    generate_scenario_dataset("c:/Users/chedu/OneDrive/Desktop/energy/backend/data/simulated_scenarios.xlsx")
