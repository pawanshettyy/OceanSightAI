from app import db
from datetime import datetime
from sqlalchemy import Text, Float, Integer, String, DateTime, Boolean

class OceanData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    salinity = db.Column(db.Float)
    ph_level = db.Column(db.Float)
    oxygen_level = db.Column(db.Float)
    current_speed = db.Column(db.Float)
    current_direction = db.Column(db.Float)
    depth = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    location_name = db.Column(db.String(100))

class Species(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scientific_name = db.Column(db.String(100), nullable=False)
    common_name = db.Column(db.String(100))
    species_type = db.Column(db.String(50))  # fish, mammal, invertebrate, etc.
    conservation_status = db.Column(db.String(50))
    habitat = db.Column(db.String(200))
    depth_range = db.Column(db.String(50))
    geographic_range = db.Column(db.Text)
    population_trend = db.Column(db.String(20))  # increasing, decreasing, stable, unknown
    threat_level = db.Column(db.String(20))  # low, medium, high, critical
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FisheriesData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    species_id = db.Column(db.Integer, db.ForeignKey('species.id'), nullable=False)
    catch_amount = db.Column(db.Float, nullable=False)  # in tons
    fishing_area = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    fishing_method = db.Column(db.String(50))
    vessel_type = db.Column(db.String(50))
    catch_date = db.Column(db.DateTime, nullable=False)
    quota_limit = db.Column(db.Float)  # maximum allowed catch
    sustainability_score = db.Column(db.Float)  # 0-100 scale
    
    species = db.relationship('Species', backref='catches')

class BiodiversityIndex(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    region_name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    species_count = db.Column(db.Integer)
    endemic_species = db.Column(db.Integer)
    threatened_species = db.Column(db.Integer)
    biodiversity_score = db.Column(db.Float)  # 0-100 scale
    ecosystem_health = db.Column(db.String(20))  # excellent, good, fair, poor, critical
    assessment_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alert_type = db.Column(db.String(50), nullable=False)  # overfishing, temperature_anomaly, biodiversity_risk
    severity = db.Column(db.String(20))  # low, medium, high, critical
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)

class SpeciesObservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    species_id = db.Column(db.Integer, db.ForeignKey('species.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    observation_count = db.Column(db.Integer, default=1)
    confidence_level = db.Column(db.Float)  # AI confidence 0-100
    observation_method = db.Column(db.String(50))  # visual, camera, sonar, etc.
    observer_type = db.Column(db.String(50))  # researcher, citizen, ai_system
    observation_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    species = db.relationship('Species', backref='observations')
