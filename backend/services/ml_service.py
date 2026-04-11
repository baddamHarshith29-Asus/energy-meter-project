import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime, timedelta

class MLService:
    @staticmethod
    def predict_future_usage(usage_data_list, days_ahead=30):
        if len(usage_data_list) < 10:
            return None
            
        df = pd.DataFrame([{
            'timestamp': d.timestamp,
            'units': d.units_kwh
        } for d in usage_data_list])
        
        df['timestamp_ordinal'] = df['timestamp'].map(datetime.toordinal)
        
        X = df[['timestamp_ordinal']].values
        y = df['units'].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        last_date = df['timestamp'].max()
        future_dates = [last_date + timedelta(days=i) for i in range(1, days_ahead + 1)]
        future_ordinals = np.array([d.toordinal() for d in future_dates]).reshape(-1, 1)
        
        predictions = model.predict(future_ordinals)
        
        return {str(d.date()): round(p, 2) for d, p in zip(future_dates, predictions)}

    @staticmethod
    def simulate_savings(current_usage, reduction_percent):
        reduction_factor = (100 - reduction_percent) / 100
        predicted_usage = current_usage * reduction_factor
        savings = current_usage - predicted_usage
        return {
            'original_usage': round(current_usage, 2),
            'new_usage': round(predicted_usage, 2),
            'savings': round(savings, 2)
        }

    @staticmethod
    def run_unified_simulation(input_data, scenario_data):
        """
        Multi-Factor Simulation Engine
        ================================
        Energy is broken into 3 independent components:

          1. Base Load    — Lighting, computers, always-on systems
                           = employees × working_hours × 0.5 kWh / (employee·hr)

          2. Machine Load — Industrial equipment during active runtime
                           = machines × machine_runtime × 2.0 kW

          3. Operational  — AC/HVAC, ambient systems, environment overhead
                           = working_hours × 1.8 kWh / hr (facility-wide)

        Proportions are derived from the formula and then mapped against the
        user's actual reported monthly_units so the outputs stay grounded in reality.

        Scenarios only affect the components they logically touch:
          - reduce_runtime → Machine Load only
          - reduce_hours   → Base Load + Operational Load only
        """
        # ── Inputs ────────────────────────────────────────────────────────────
        machines     = max(float(input_data.get('machines', 1)), 1)
        runtime      = max(float(input_data.get('machineRuntime', 1)), 0)
        mon_units    = max(float(input_data.get('monthlyUnits', 1)), 1)
        cost_unit    = max(float(input_data.get('costPerUnit', 1)), 0.01)
        employees    = max(float(input_data.get('employees', 1)), 1)
        working_hours= max(float(input_data.get('workingHours', 8)), 1)
        working_days = max(float(input_data.get('workingDays', 22)), 1)

        # ── Scenario ──────────────────────────────────────────────────────────
        reduce_runtime_pct = min(float(scenario_data.get('reduceRuntime', 0)), 100)
        reduce_hours       = min(float(scenario_data.get('reduceHours', 0)), working_hours - 1)

        # ── Theoretical Daily Load Calculation ────────────────────────────────
        # These numbers represent the relative "weight" of each component
        BASE_RATE        = 0.5   # kWh per employee per hour
        MACHINE_POWER_KW = 2.0   # kWh per machine per runtime hour
        OPERATIONAL_RATE = 1.8   # kWh per facility operating hour/day

        daily_base        = employees    * working_hours * BASE_RATE
        daily_machine     = machines     * runtime       * MACHINE_POWER_KW
        daily_operational = working_hours * OPERATIONAL_RATE

        theoretical_daily = daily_base + daily_machine + daily_operational

        # ── Proportional Mapping onto Actual Reported Units ───────────────────
        # Anchors the formula output to the user's real electricity bill
        monthly_theoretical = theoretical_daily * working_days
        if monthly_theoretical > 0:
            calibration = mon_units / monthly_theoretical
        else:
            calibration = 1.0

        base_units        = daily_base        * working_days * calibration
        machine_units     = daily_machine     * working_days * calibration
        operational_units = daily_operational * working_days * calibration

        baseline_bill = mon_units * cost_unit

        # ── Apply Targeted Scenario Reductions ────────────────────────────────
        # Machine Load: directly reduced by the runtime % slider
        new_machine_units = machine_units * (1.0 - reduce_runtime_pct / 100.0)

        # Base Load & Operational: reduced by the hour cut (fewer hours = less lighting/AC/computers)
        if working_hours > 0:
            hour_fraction = (working_hours - reduce_hours) / working_hours
        else:
            hour_fraction = 1.0
        hour_fraction = max(0.0, hour_fraction)

        new_base_units        = base_units        * hour_fraction
        new_operational_units = operational_units * hour_fraction

        new_total_units = new_base_units + new_machine_units + new_operational_units
        new_bill        = new_total_units * cost_unit
        savings         = baseline_bill - new_bill

        # ── Per-Component Reduction % (for breakdown display) ─────────────────
        base_reduction        = round((base_units - new_base_units) / base_units * 100, 1)        if base_units > 0        else 0
        machine_reduction     = round((machine_units - new_machine_units) / machine_units * 100, 1) if machine_units > 0     else 0
        operational_reduction = round((operational_units - new_operational_units) / operational_units * 100, 1) if operational_units > 0 else 0

        # ── Who contributed most to savings? ──────────────────────────────────
        base_saved        = base_units - new_base_units
        machine_saved     = machine_units - new_machine_units
        operational_saved = operational_units - new_operational_units
        total_saved       = base_saved + machine_saved + operational_saved

        def pct(v): return round(v / total_saved * 100, 1) if total_saved > 0 else 0

        insight_parts = []
        if machine_reduction > 0: insight_parts.append(f"Machine load cut {machine_reduction}% (contributed {pct(machine_saved)}% of savings)")
        if base_reduction > 0:    insight_parts.append(f"Base load reduced {base_reduction}% (contributed {pct(base_saved)}% of savings)")
        if operational_reduction > 0: insight_parts.append(f"Operational load down {operational_reduction}% (contributed {pct(operational_saved)}% of savings)")
        auto_insight = ". ".join(insight_parts) + "." if insight_parts else "No scenario adjustments applied."

        # ── Upgraded Efficiency Score ─────────────────────────────────────────
        savings_pct        = savings / baseline_bill * 100 if baseline_bill > 0 else 0
        machine_load_pct   = machine_units / mon_units * 100 if mon_units > 0 else 0
        machine_penalty    = max(0, machine_load_pct - 60) * 0.3   # penalize if >60% machine-dependent
        peak_penalty       = max(0, working_hours - 8) * 1.5        # extra hours add penalty
        score = 60 + savings_pct - machine_penalty - peak_penalty
        score = round(min(99.0, max(10.0, score)), 1)

        return {
            "baseline": {
                "units": round(mon_units, 1),
                "bill":  round(baseline_bill, 2),
                "breakdown": {
                    "base":        round(base_units, 1),
                    "machine":     round(machine_units, 1),
                    "operational": round(operational_units, 1)
                }
            },
            "simulated": {
                "units":   round(new_total_units, 1),
                "bill":    round(new_bill, 2),
                "savings": round(savings, 2),
                "score":   score,
                "breakdown": {
                    "base":        round(new_base_units, 1),
                    "machine":     round(new_machine_units, 1),
                    "operational": round(new_operational_units, 1)
                },
                "reductions": {
                    "base_pct":        base_reduction,
                    "machine_pct":     machine_reduction,
                    "operational_pct": operational_reduction
                }
            },
            "auto_insight": auto_insight,
            "chart_data": [
                {"name": "Baseline", "Units": round(mon_units, 1),        "Cost": round(baseline_bill, 1)},
                {"name": "Simulated","Units": round(new_total_units, 1),  "Cost": round(new_bill, 1)}
            ],
            "breakdown_chart": [
                {"component": "Base Load",       "Baseline": round(base_units, 1),        "Simulated": round(new_base_units, 1)},
                {"component": "Machine Load",    "Baseline": round(machine_units, 1),     "Simulated": round(new_machine_units, 1)},
                {"component": "Operational",     "Baseline": round(operational_units, 1), "Simulated": round(new_operational_units, 1)}
            ]
        }

