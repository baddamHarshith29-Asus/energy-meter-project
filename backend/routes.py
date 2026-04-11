from flask import Blueprint, request, jsonify, send_file
from database import db
from models import BusinessProfile, SimulationScenario
from services.ml_service import MLService
from services.ai_service import AIService
from services.ocr_service import OCRService
from services.report_service import ReportService
from services.analytics import AdvancedAnalytics
import io
import os

api = Blueprint('api', __name__)
ai_service = AIService()
ocr_service = OCRService()

# ─── AI Chat ──────────────────────────────────────────────────────────────────
@api.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_query = data.get('query')
    history = data.get('history', [])
    context = data.get('context', None)
    response = ai_service.chat_assistant(user_query, history, context)
    return jsonify({'response': response})

# ─── Unified Simulation ────────────────────────────────────────────────────────
@api.route('/simulate-unified', methods=['POST'])
def simulate_unified():
    data = request.json
    if not data:
        return jsonify({"error": "No input provided"}), 400
    input_data = data.get('input', {})
    scenario_data = data.get('scenario', {})
    try:
        result = MLService.run_unified_simulation(input_data, scenario_data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Simulation failed: {str(e)}"}), 500

# ─── Feature 1: Bill / CSV Upload & Auto-Analysis ─────────────────────────────
@api.route('/analyze-upload', methods=['POST'])
def analyze_upload():
    """
    Accept a CSV or Excel file containing monthly electricity usage.
    Automatically detect columns, compute stats, and return prefill data
    so the user does not have to type anything manually.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if not file.filename:
        return jsonify({'error': 'Empty filename'}), 400
    
    summary, error = ReportService.analyze_uploaded_file(file.stream, file.filename)
    if error:
        return jsonify({'error': error}), 422
    
    return jsonify(summary), 200

# ─── Feature 2: AI Carbon Footprint PDF Report Generator ─────────────────────
@api.route('/generate-carbon-report', methods=['POST'])
def generate_carbon_report():
    """
    Generate a professional PDF sustainability + carbon footprint report.
    Accepts the current simulation context and an AI summary.
    Returns a downloadable PDF file.
    """
    data = request.json or {}
    
    baseline = data.get('baseline', {})
    simulated = data.get('simulated', {})
    scenario = data.get('scenario', {})
    business_name = data.get('business_name', 'Your Business')
    
    # Get a quick AI narrative for the report
    sim_context = {'baseline': baseline, 'simulated': simulated}
    ai_summary = ai_service.chat_assistant(
        "Write a 3-4 sentence executive summary explaining the energy savings achieved "
        "by this simulation scenario. Be professional, specific, and include the dollar savings.",
        context=sim_context
    )
    
    pdf_bytes, error = ReportService.generate_pdf_report(
        business_name=business_name,
        baseline=baseline,
        simulated=simulated,
        scenario=scenario,
        ai_summary=ai_summary
    )
    
    if error:
        return jsonify({'error': error}), 500
    
    return send_file(
        io.BytesIO(pdf_bytes),
        download_name=f"carbon_report_{business_name.replace(' ', '_')}.pdf",
        as_attachment=True,
        mimetype='application/pdf'
    )

# ─── OCR Bill Scan (existing) ─────────────────────────────────────────────────
@api.route('/scan-bill', methods=['POST'])
def scan_bill():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400
    os.makedirs("temp", exist_ok=True)
    temp_path = os.path.join("temp", file.filename)
    file.save(temp_path)
    try:
        scan_results = ocr_service.scan_bill(temp_path)
        return jsonify(scan_results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

# ─── Feature: Predictive Forecasting ──────────────────────────────────────────
@api.route('/predict-costs', methods=['POST'])
def predict_costs():
    data = request.json or {}
    baseline_bill = float(data.get('baseline_bill', 0))
    simulated_bill = float(data.get('simulated_bill', 0))
    months = int(data.get('months', 6))
    inflation = float(data.get('inflation_rate', 0.05))
    result = AdvancedAnalytics.predict_costs(baseline_bill, simulated_bill, months, inflation)
    return jsonify(result), 200

# ─── Feature: Industry Benchmarking ───────────────────────────────────────────
@api.route('/benchmark', methods=['POST'])
def benchmark():
    data = request.json or {}
    monthly_units = float(data.get('monthly_units', 0))
    employees = int(data.get('employees', 1))
    industry = data.get('industry', 'default')
    result = AdvancedAnalytics.benchmark(monthly_units, employees, industry)
    return jsonify(result), 200

# ─── Feature: ROI Payback Calculator ──────────────────────────────────────────
@api.route('/calculate-roi', methods=['POST'])
def calculate_roi():
    data = request.json or {}
    monthly_savings = float(data.get('monthly_savings', 0))
    result = AdvancedAnalytics.calculate_roi(monthly_savings)
    return jsonify(result), 200

# ─── Feature: Anomaly Detection ──────────────────────────────────────────────
@api.route('/detect-anomalies', methods=['POST'])
def detect_anomalies():
    data = request.json or {}
    usage_data = data.get('usage_data', [])
    threshold = float(data.get('threshold', 1.5))
    result = AdvancedAnalytics.detect_anomalies(usage_data, threshold)
    return jsonify(result), 200
