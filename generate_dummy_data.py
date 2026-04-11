import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_bills():
    print("Generating 60 months of realistic factory electricity bills...")
    
    data = []
    # Start 60 months ago
    start_date = datetime.now() - timedelta(days=60*30)
    
    # Base parameters for an industrial factory
    base_kwh = 750
    rate_per_kwh = 8.1  # cost per unit
    
    for i in range(60):
        # Calculate month
        current_date = start_date + timedelta(days=30*i)
        month_str = current_date.strftime("%Y-%m")
        
        # Add random realistic fluctuations (-10% to +15% based on "factory demand")
        fluctuation = random.uniform(-0.10, 0.15)
        
        # Summer months (April-July) usage is higher due to ambient cooling
        if current_date.month in [4, 5, 6, 7]:
            fluctuation += 0.08
            
        units_consumed = round(base_kwh * (1 + fluctuation))
        total_bill = round(units_consumed * rate_per_kwh)
        
        data.append({
            "Month": month_str,
            "Consumption": units_consumed,
            "Bill": total_bill
        })
        
    df = pd.DataFrame(data)
    
    # Save to the main project folder
    file_path = "sample_factory_bills.csv"
    df.to_csv(file_path, index=False)
    
    print(f"✅ Success! Generated '{file_path}' seamlessly.")
    print("You can now upload this directly into the Dashboard!")

if __name__ == "__main__":
    generate_bills()
