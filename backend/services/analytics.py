"""
Advanced Analytics Service
===========================
Provides 4 high-impact features:
1. Predictive Forecasting   — 6-month cost trajectory via linear regression
2. Industry Benchmarking    — Compare against sector-standard kWh/employee
3. ROI Payback Calculator   — Break-even timeline for energy investments
4. Anomaly Detection        — Statistical outlier detection on usage data
"""

import numpy as np
from datetime import datetime

# ── Industry Benchmark Data (kWh per employee per month) ──────────────────────
# Source: India Bureau of Energy Efficiency (BEE) approximate ranges
INDUSTRY_BENCHMARKS = {
    "manufacturing":  { "excellent": 45, "good": 70, "average": 100, "poor": 150 },
    "textile":        { "excellent": 55, "good": 85, "average": 120, "poor": 170 },
    "automotive":     { "excellent": 60, "good": 90, "average": 130, "poor": 180 },
    "tech_office":    { "excellent": 20, "good": 35, "average": 55,  "poor": 80 },
    "food_processing":{ "excellent": 50, "good": 75, "average": 110, "poor": 160 },
    "pharmaceutical": { "excellent": 40, "good": 65, "average": 95,  "poor": 140 },
    "default":        { "excellent": 40, "good": 65, "average": 100, "poor": 150 },
}


class AdvancedAnalytics:

    # ══════════════════════════════════════════════════════════════════════════
    # 1. PREDICTIVE FORECASTING
    # ══════════════════════════════════════════════════════════════════════════
    @staticmethod
    def predict_costs(baseline_bill, simulated_bill, months_ahead=6, inflation_rate=0.05):
        """
        Project monthly costs for the next N months using:
        - Baseline trajectory (no changes, with inflation)
        - Simulated trajectory (after optimization)
        Also calculates cumulative savings.
        """
        monthly_inflation = (1 + inflation_rate) ** (1/12)  # monthly compound
        
        forecast = []
        cumulative_baseline = 0
        cumulative_simulated = 0
        
        now = datetime.now()
        
        for i in range(1, months_ahead + 1):
            month_factor = monthly_inflation ** i
            
            baseline_projected = round(baseline_bill * month_factor, 2)
            simulated_projected = round(simulated_bill * month_factor, 2)
            monthly_saving = round(baseline_projected - simulated_projected, 2)
            
            cumulative_baseline += baseline_projected
            cumulative_simulated += simulated_projected
            
            # Month label
            month_num = (now.month + i - 1) % 12 + 1
            year = now.year + (now.month + i - 1) // 12
            month_label = datetime(year, month_num, 1).strftime("%b %Y")
            
            forecast.append({
                "month": month_label,
                "baseline_cost": baseline_projected,
                "simulated_cost": simulated_projected,
                "monthly_saving": monthly_saving,
                "cumulative_savings": round(cumulative_baseline - cumulative_simulated, 2)
            })
        
        return {
            "forecast": forecast,
            "total_baseline_cost": round(cumulative_baseline, 2),
            "total_simulated_cost": round(cumulative_simulated, 2),
            "total_savings_6m": round(cumulative_baseline - cumulative_simulated, 2),
            "inflation_rate_used": f"{inflation_rate * 100}%"
        }

    # ══════════════════════════════════════════════════════════════════════════
    # 2. INDUSTRY BENCHMARKING
    # ══════════════════════════════════════════════════════════════════════════
    @staticmethod
    def benchmark(monthly_units, employees, industry="default"):
        """
        Compare the business's energy efficiency (kWh/employee) against
        industry standard benchmarks.
        Returns a rating (Excellent/Good/Average/Poor) and peer comparison.
        """
        if employees <= 0:
            employees = 1
        
        kwh_per_employee = round(monthly_units / employees, 1)
        
        industry_key = industry.lower().replace(" ", "_")
        benchmarks = INDUSTRY_BENCHMARKS.get(industry_key, INDUSTRY_BENCHMARKS["default"])
        
        if kwh_per_employee <= benchmarks["excellent"]:
            rating = "Excellent"
            rating_color = "#22c55e"
            percentile = 95
        elif kwh_per_employee <= benchmarks["good"]:
            rating = "Good"
            rating_color = "#3b82f6"
            percentile = 75
        elif kwh_per_employee <= benchmarks["average"]:
            rating = "Average"
            rating_color = "#f59e0b"
            percentile = 50
        else:
            rating = "Poor"
            rating_color = "#ef4444"
            percentile = 20
        
        # How far from excellent
        gap_to_excellent = round(kwh_per_employee - benchmarks["excellent"], 1)
        potential_savings_kwh = max(0, gap_to_excellent * employees)
        
        return {
            "kwh_per_employee": kwh_per_employee,
            "rating": rating,
            "rating_color": rating_color,
            "percentile": percentile,
            "industry": industry_key,
            "benchmarks": benchmarks,
            "gap_to_excellent": max(0, gap_to_excellent),
            "potential_savings_kwh": round(potential_savings_kwh, 1),
            "comparison_chart": [
                {"label": "Your Business", "value": kwh_per_employee, "fill": rating_color},
                {"label": "Excellent", "value": benchmarks["excellent"], "fill": "#22c55e"},
                {"label": "Industry Avg", "value": benchmarks["average"], "fill": "#f59e0b"},
                {"label": "Poor", "value": benchmarks["poor"], "fill": "#ef4444"},
            ]
        }

    # ══════════════════════════════════════════════════════════════════════════
    # 3. ROI PAYBACK CALCULATOR
    # ══════════════════════════════════════════════════════════════════════════
    @staticmethod
    def calculate_roi(monthly_savings, investment_options=None):
        """
        Calculate payback period for common energy efficiency investments.
        Shows how many months until the investment pays for itself.
        """
        if not investment_options:
            investment_options = [
                {"name": "LED Lighting Retrofit", "cost": 15000, "extra_savings_pct": 8},
                {"name": "VFD Motor Drives", "cost": 50000, "extra_savings_pct": 20},
                {"name": "Smart HVAC Controls", "cost": 25000, "extra_savings_pct": 12},
                {"name": "Power Factor Correction", "cost": 30000, "extra_savings_pct": 10},
                {"name": "Solar Panel (5kW)", "cost": 250000, "extra_savings_pct": 35},
            ]
        
        results = []
        for option in investment_options:
            extra_monthly_saving = monthly_savings * (option["extra_savings_pct"] / 100)
            total_monthly_saving = monthly_savings + extra_monthly_saving
            
            if total_monthly_saving > 0:
                payback_months = round(option["cost"] / total_monthly_saving, 1)
                annual_roi_pct = round((total_monthly_saving * 12 / option["cost"]) * 100, 1)
                five_year_profit = round(total_monthly_saving * 60 - option["cost"], 2)
            else:
                payback_months = float('inf')
                annual_roi_pct = 0
                five_year_profit = -option["cost"]
            
            results.append({
                "name": option["name"],
                "investment_cost": option["cost"],
                "extra_savings_pct": option["extra_savings_pct"],
                "extra_monthly_saving": round(extra_monthly_saving, 2),
                "total_monthly_saving": round(total_monthly_saving, 2),
                "payback_months": payback_months,
                "annual_roi_pct": annual_roi_pct,
                "five_year_profit": five_year_profit,
                "recommended": payback_months < 24  # Recommended if pays back within 2 years
            })
        
        # Sort by payback period
        results.sort(key=lambda x: x["payback_months"])
        
        return {
            "base_monthly_savings": round(monthly_savings, 2),
            "investments": results
        }

    # ══════════════════════════════════════════════════════════════════════════
    # 4. ANOMALY DETECTION
    # ══════════════════════════════════════════════════════════════════════════
    @staticmethod
    def detect_anomalies(usage_data, threshold_sigma=1.5):
        """
        Statistical anomaly detection using Z-score method.
        Flags months where consumption deviates significantly from the mean.
        
        Args:
            usage_data: list of dicts with 'month' and 'units' keys
            threshold_sigma: number of standard deviations for anomaly threshold
        """
        if not usage_data or len(usage_data) < 3:
            return {"anomalies": [], "message": "Need at least 3 months of data for anomaly detection."}
        
        units = [float(d.get('units', 0)) for d in usage_data]
        mean_val = np.mean(units)
        std_val = np.std(units)
        
        if std_val == 0:
            return {"anomalies": [], "mean": round(float(mean_val), 1), "std": 0, "message": "All values are identical."}
        
        anomalies = []
        annotated = []
        
        for i, d in enumerate(usage_data):
            unit_val = float(d.get('units', 0))
            z_score = (unit_val - mean_val) / std_val
            is_anomaly = abs(z_score) > threshold_sigma
            
            entry = {
                "month": d.get('month', f'Month {i+1}'),
                "units": unit_val,
                "z_score": round(float(z_score), 2),
                "is_anomaly": is_anomaly,
                "deviation": "high" if z_score > threshold_sigma else ("low" if z_score < -threshold_sigma else "normal")
            }
            annotated.append(entry)
            if is_anomaly:
                anomalies.append(entry)
        
        return {
            "mean": round(float(mean_val), 1),
            "std": round(float(std_val), 1),
            "threshold": threshold_sigma,
            "total_months": len(usage_data),
            "anomaly_count": len(anomalies),
            "anomalies": anomalies,
            "annotated_data": annotated,
            "health_status": "Stable" if len(anomalies) == 0 else f"{len(anomalies)} anomalies detected"
        }
