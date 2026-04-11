from database import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BusinessProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    business_name = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(50))
    employees = db.Column(db.Integer)
    working_days = db.Column(db.Integer)
    working_hours = db.Column(db.Integer)
    machines = db.Column(db.Integer)
    machine_runtime = db.Column(db.Integer)
    monthly_units = db.Column(db.Float)
    cost_per_unit = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    scenarios = db.relationship('SimulationScenario', backref='business', lazy=True)

class SimulationScenario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    business_profile_id = db.Column(db.Integer, db.ForeignKey('business_profile.id'), nullable=False)
    scenario_name = db.Column(db.String(100), default="Base Optimization")
    reduce_runtime_pct = db.Column(db.Float, default=0.0)
    reduce_hours = db.Column(db.Float, default=0.0)
    projected_savings = db.Column(db.Float)
    efficiency_score = db.Column(db.Float)
    ai_explanation = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
