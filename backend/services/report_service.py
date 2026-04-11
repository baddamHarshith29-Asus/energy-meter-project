import io
import re
from datetime import datetime
from services.ml_service import MLService

# India grid average CO2 emission factor: 0.82 kg CO2 per kWh
INDIA_CO2_FACTOR = 0.82  # kg CO2 per kWh

def sanitize_text(text):
    """Remove non-latin1 characters that fpdf core fonts cannot handle."""
    if not text:
        return ""
    # Replace common unicode with ASCII equivalents
    replacements = {
        '\u2019': "'", '\u2018': "'", '\u201c': '"', '\u201d': '"',
        '\u2013': '-', '\u2014': '-', '\u2026': '...', '\u2022': '*',
        '\u00b7': '*', '\u2032': "'", '\u2033': '"', '\u00a0': ' ',
        '\u2010': '-', '\u2011': '-', '\u2012': '-',
        '\u00b0': ' deg', '\u00b2': '2', '\u00b3': '3',
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    # Strip any remaining non-latin1 chars
    text = text.encode('latin-1', errors='replace').decode('latin-1')
    return text


class ReportService:

    @staticmethod
    def calculate_carbon(units_kwh):
        """Calculate CO2 emissions from kWh usage."""
        kg_co2 = units_kwh * INDIA_CO2_FACTOR
        trees_equivalent = kg_co2 / 21.77  # avg tree absorbs 21.77 kg CO2/year
        car_km_equivalent = kg_co2 / 0.21  # avg car emits 0.21 kg CO2/km
        return {
            "kg_co2": round(kg_co2, 2),
            "trees_needed": round(trees_equivalent, 1),
            "car_km_equivalent": round(car_km_equivalent, 1),
            "tonnes_co2": round(kg_co2 / 1000, 3)
        }

    @staticmethod
    def generate_pdf_report(business_name, baseline, simulated, scenario, ai_summary):
        """Generate a professional PDF sustainability report."""
        try:
            from fpdf import FPDF
        except ImportError:
            return None, "fpdf2 not installed. Run: pip install fpdf2"
        
        baseline_units = float(baseline.get('units', 0))
        simulated_units = float(simulated.get('units', 0))
        baseline_bill = float(baseline.get('bill', 0))
        simulated_bill = float(simulated.get('bill', 0))
        savings = float(simulated.get('savings', 0))
        score = float(simulated.get('score', 0))

        baseline_carbon = ReportService.calculate_carbon(baseline_units)
        simulated_carbon = ReportService.calculate_carbon(simulated_units)
        co2_saved = round(baseline_carbon['kg_co2'] - simulated_carbon['kg_co2'], 2)

        # Sanitize all text inputs
        business_name = sanitize_text(str(business_name))
        ai_summary = sanitize_text(str(ai_summary)) if ai_summary else "No AI summary provided."

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # ── Header ────────────────────────────────
        pdf.set_fill_color(15, 23, 42)
        pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_text_color(0, 200, 255)
        pdf.set_font("Helvetica", "B", 20)
        pdf.set_xy(10, 10)
        pdf.cell(0, 10, "AI Energy Simulation Platform", ln=True)
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(180, 180, 200)
        pdf.cell(0, 8, sanitize_text(f"Carbon Footprint & Sustainability Report - {business_name}"), ln=True)
        
        # Metadata
        pdf.set_xy(10, 46)
        pdf.set_text_color(100, 100, 120)
        pdf.set_font("Helvetica", "", 8)
        pdf.cell(0, 5, sanitize_text(f"Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')} | Powered by Llama-3 AI + Digital Twin Physics Engine"), ln=True)
        pdf.ln(4)
        
        # ── Helper functions ──────────────────────
        def section_header(title):
            pdf.set_fill_color(30, 64, 175)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 8, sanitize_text(f"  {title}"), ln=True, fill=True)
            pdf.set_text_color(30, 30, 50)
            pdf.set_font("Helvetica", "", 10)
            pdf.ln(2)
        
        def kv_row(label, value, unit=""):
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(90, 90, 120)
            pdf.cell(80, 7, sanitize_text(label), ln=False)
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(20, 20, 40)
            pdf.cell(0, 7, sanitize_text(f"{value} {unit}"), ln=True)
        
        # ── Section 1 ────────────────────────────
        section_header("1. Baseline Energy Profile (Current State)")
        kv_row("Monthly Consumption:", f"{baseline_units:,.1f}", "kWh")
        kv_row("Monthly Electricity Cost:", f"${baseline_bill:,.2f}")
        kv_row("Carbon Footprint:", f"{baseline_carbon['kg_co2']:,}", "kg CO2/month")
        kv_row("Trees Needed to Offset:", f"{baseline_carbon['trees_needed']:,}", "trees/year")
        kv_row("Equivalent Car Distance:", f"{baseline_carbon['car_km_equivalent']:,.0f}", "km driven")
        
        pdf.ln(3)
        section_header("2. Simulated Scenario Results (Optimized)")
        kv_row("Projected Consumption:", f"{simulated_units:,.1f}", "kWh")
        kv_row("Projected Monthly Cost:", f"${simulated_bill:,.2f}")
        kv_row("Carbon Footprint:", f"{simulated_carbon['kg_co2']:,}", "kg CO2/month")
        kv_row("Efficiency Score:", f"{score}/100")

        # Breakdown if available
        baseline_bd = baseline.get('breakdown', {})
        simulated_bd = simulated.get('breakdown', {})
        if baseline_bd:
            pdf.ln(3)
            section_header("3. Component Breakdown Analysis")
            kv_row("Base Load (Before):", f"{baseline_bd.get('base', 0):,.1f}", "kWh")
            kv_row("Base Load (After):", f"{simulated_bd.get('base', 0):,.1f}", "kWh")
            kv_row("Machine Load (Before):", f"{baseline_bd.get('machine', 0):,.1f}", "kWh")
            kv_row("Machine Load (After):", f"{simulated_bd.get('machine', 0):,.1f}", "kWh")
            kv_row("Operational (Before):", f"{baseline_bd.get('operational', 0):,.1f}", "kWh")
            kv_row("Operational (After):", f"{simulated_bd.get('operational', 0):,.1f}", "kWh")
            next_sect = 4
        else:
            next_sect = 3
        
        pdf.ln(3)
        section_header(f"{next_sect}. Projected Savings & Impact")
        kv_row("Monthly Cost Savings:", f"${savings:,.2f}")
        kv_row("Annual Cost Savings:", f"${savings * 12:,.2f}")
        kv_row("Monthly CO2 Reduction:", f"{co2_saved:,}", "kg CO2")
        kv_row("Annual CO2 Reduction:", f"{co2_saved * 12:,}", "kg CO2")
        annual_trees = round((co2_saved * 12) / 21.77, 1) if co2_saved > 0 else 0
        kv_row("Annual Trees Offset:", f"{annual_trees:,}", "trees")
        
        pdf.ln(4)
        section_header(f"{next_sect + 1}. AI Executive Analysis")
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(30, 30, 60)
        pdf.multi_cell(0, 5, ai_summary)
        
        pdf.ln(4)
        section_header(f"{next_sect + 2}. Recommendation")
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(30, 30, 60)
        if savings > 0:
            recommendation = sanitize_text(
                f"Based on simulation results, implementing the proposed changes "
                f"is HIGHLY RECOMMENDED. Monthly savings of ${savings:,.2f} and "
                f"a {co2_saved:,.1f} kg CO2 reduction contributes to both cost efficiency "
                f"and ESG sustainability targets. Prioritize machine runtime reduction "
                f"and evaluate operating schedules quarterly."
            )
        else:
            recommendation = "Current parameters appear optimized. Continue monitoring."
        pdf.multi_cell(0, 5, recommendation)
        
        # Footer
        pdf.set_y(-18)
        pdf.set_font("Helvetica", "I", 7)
        pdf.set_text_color(140, 140, 160)
        pdf.cell(0, 5, "AI Energy Simulation Platform | Confidential Report | CO2 factors: India CEA Grid Emission Standard", align="C")
        
        pdf_bytes = pdf.output()
        return bytes(pdf_bytes), None

    @staticmethod
    def analyze_uploaded_file(file_stream, filename):
        """Parse an uploaded CSV/Excel bill and extract stats for simulation pre-fill."""
        import pandas as pd
        
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(file_stream)
            elif filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_stream)
            else:
                return None, "Unsupported file type. Please upload CSV or Excel."
        except Exception as e:
            return None, f"Error reading file: {str(e)}"
        
        df.columns = [str(c).strip().lower().replace(' ', '_') for c in df.columns]
        
        col_map = {
            'units': ['units', 'units_kwh', 'kwh', 'consumption', 'energy', 'units_consumed', 'monthly_units'],
            'cost': ['cost', 'bill', 'amount', 'charges', 'total_cost', 'electricity_bill'],
            'date': ['date', 'month', 'period', 'billing_date', 'timestamp'],
        }
        
        found = {}
        for key, aliases in col_map.items():
            for alias in aliases:
                if alias in df.columns:
                    found[key] = alias
                    break
        
        if 'units' not in found:
            return None, "Could not detect a units/kWh column. Ensure your file has a column named 'units', 'kwh', or 'consumption'."
        
        units_col = found['units']
        units_series = pd.to_numeric(df[units_col], errors='coerce').dropna()
        
        avg_monthly_units = round(float(units_series.mean()), 1)
        total_units = round(float(units_series.sum()), 1)
        max_units = round(float(units_series.max()), 1)
        min_units = round(float(units_series.min()), 1)
        
        avg_cost_per_unit = 8.0
        avg_monthly_cost = None
        
        if 'cost' in found:
            cost_series = pd.to_numeric(df[found['cost']], errors='coerce').dropna()
            if len(cost_series) > 0 and float(units_series.mean()) > 0:
                avg_monthly_cost = round(float(cost_series.mean()), 2)
                avg_cost_per_unit = round(float(cost_series.mean()) / float(units_series.mean()), 3)
        
        # Trend analysis
        trend = "stable"
        if len(units_series) >= 3:
            recent = units_series.tail(3).mean()
            older = units_series.head(3).mean()
            if recent > older * 1.1:
                trend = "increasing"
            elif recent < older * 0.9:
                trend = "decreasing"
        
        summary = {
            "rows_detected": len(df),
            "avg_monthly_units": avg_monthly_units,
            "total_units": total_units,
            "max_units": max_units,
            "min_units": min_units,
            "avg_cost_per_unit": avg_cost_per_unit,
            "avg_monthly_cost": avg_monthly_cost,
            "consumption_trend": trend,
            "columns_detected": list(df.columns),
            "prefill": {
                "monthlyUnits": avg_monthly_units,
                "costPerUnit": avg_cost_per_unit
            }
        }
        
        return summary, None
