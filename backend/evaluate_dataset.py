import pandas as pd
from services.ml_service import MLService
from services.ai_service import AIService
import time

def evaluate_scenarios():
    print("Loading raw scenarios...")
    input_df = pd.read_excel('c:/Users/chedu/OneDrive/Desktop/energy/backend/data/simulated_scenarios.xlsx')
    
    # We will process a subset to avoid hitting Groq API rate limits instantly
    # Change to len(input_df) to process all, but 10 is safe for a fast demo.
    limit = 10
    df = input_df.head(limit).copy()
    
    ai = AIService()
    
    projected_savings_col = []
    efficiency_score_col = []
    ai_explanation_col = []
    
    print(f"Evaluating {len(df)} scenarios through Mathematics & AI Engine...")
    
    for index, row in df.iterrows():
        # 1. Prepare raw data for the physics engine
        input_data = {
            'machines': row['machines'],
            'machineRuntime': row['machine_runtime'],
            'monthlyUnits': row['monthly_units'],
            'costPerUnit': row['cost_per_unit'],
            'workingHours': row['working_hours']
        }
        scenario_data = {
            'reduceRuntime': row['scenario_reduce_runtime_pct'],
            'reduceHours': row['scenario_reduce_hours']
        }
        
        # 2. Physics Engine Evaluation
        result = MLService.run_unified_simulation(input_data, scenario_data)
        
        simulated = result.get('simulated', {})
        baseline = result.get('baseline', {})
        
        savings = simulated.get('savings', 0)
        score = simulated.get('score', 0)
        
        projected_savings_col.append(savings)
        efficiency_score_col.append(score)
        
        # 3. AI Explanation Engine
        prompt = (
            f"You are evaluating a {row['industry']} scenario. "
            f"Baseline Cost: ${baseline.get('bill', 0)}. "
            f"Simulated Cost: ${simulated.get('bill', 0)}. "
            f"Projected Monthly Savings: ${savings}. "
            f"The strategy used was reducing machine runtime by {row['scenario_reduce_runtime_pct']}% "
            f"and cutting {row['scenario_reduce_hours']} operating hours. "
            f"Write a very short, 2-sentence executive summary explaining why this works."
        )
        
        print(f"[{index+1}/{len(df)}] Querying AI for {row['business_name']}...")
        ai_response = ai.chat_assistant(user_query=prompt)
        ai_explanation_col.append(ai_response)
        
        # Slight delay to respect rate limits
        time.sleep(1)

    df['projected_savings'] = projected_savings_col
    df['efficiency_score'] = efficiency_score_col
    df['ai_explanation'] = ai_explanation_col
    
    output_path = 'c:/Users/chedu/OneDrive/Desktop/energy/backend/data/evaluated_scenarios.xlsx'
    df.to_excel(output_path, index=False)
    print(f"\nSuccessfully evaluated scenarios & saved to {output_path}")

if __name__ == "__main__":
    evaluate_scenarios()
