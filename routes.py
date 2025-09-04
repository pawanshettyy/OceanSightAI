from flask import render_template, request, jsonify, redirect, url_for, flash
from app import app, db
from models import OceanData, Species, FisheriesData, BiodiversityIndex, Alert, SpeciesObservation
from services.ocean_service import OceanService
from services.species_service import SpeciesService
from services.fisheries_service import FisheriesService
from services.biodiversity_service import BiodiversityService
from datetime import datetime, timedelta
import json

@app.route('/')
def index():
    """Main landing page"""
    # Get recent alerts
    recent_alerts = Alert.query.filter_by(is_active=True).order_by(Alert.created_at.desc()).limit(5).all()
    
    # Get basic stats for overview
    total_species = Species.query.count()
    recent_observations = SpeciesObservation.query.filter(
        SpeciesObservation.observation_date >= datetime.utcnow() - timedelta(days=30)
    ).count()
    
    return render_template('index.html', 
                         recent_alerts=recent_alerts,
                         total_species=total_species,
                         recent_observations=recent_observations)

@app.route('/dashboard')
def dashboard():
    """Main dashboard with oceanographic data visualizations"""
    return render_template('dashboard.html')

@app.route('/species')
def species():
    """Species identification and management page"""
    return render_template('species.html')

@app.route('/fisheries')
def fisheries():
    """Fisheries management and catch data page"""
    return render_template('fisheries.html')

@app.route('/alerts')
def alerts():
    """Alerts and notifications page"""
    all_alerts = Alert.query.order_by(Alert.created_at.desc()).all()
    return render_template('alerts.html', alerts=all_alerts)

# API Endpoints

@app.route('/api/ocean-data')
def get_ocean_data():
    """Get oceanographic data for visualization"""
    try:
        ocean_service = OceanService()
        
        # Get query parameters
        lat_min = request.args.get('lat_min', type=float)
        lat_max = request.args.get('lat_max', type=float)
        lng_min = request.args.get('lng_min', type=float)
        lng_max = request.args.get('lng_max', type=float)
        
        data = ocean_service.get_ocean_data_for_region(lat_min, lat_max, lng_min, lng_max)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/species-data')
def get_species_data():
    """Get species data for visualization"""
    try:
        species_service = SpeciesService()
        data = species_service.get_all_species_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/fisheries-data')
def get_fisheries_data():
    """Get fisheries catch data"""
    try:
        fisheries_service = FisheriesService()
        
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        data = fisheries_service.get_catch_data(start_date, end_date)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/biodiversity-index')
def get_biodiversity_index():
    """Get biodiversity index data"""
    try:
        biodiversity_service = BiodiversityService()
        data = biodiversity_service.get_biodiversity_indices()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/species/identify', methods=['POST'])
def identify_species():
    """Mock species identification endpoint"""
    try:
        species_service = SpeciesService()
        
        # In a real implementation, this would process an uploaded image
        # For now, we'll return a mock identification result
        result = species_service.mock_species_identification()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts')
def get_alerts():
    """Get active alerts"""
    try:
        alerts = Alert.query.filter_by(is_active=True).order_by(Alert.created_at.desc()).all()
        
        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                'id': alert.id,
                'type': alert.alert_type,
                'severity': alert.severity,
                'title': alert.title,
                'description': alert.description,
                'location': alert.location,
                'latitude': alert.latitude,
                'longitude': alert.longitude,
                'created_at': alert.created_at.isoformat()
            })
        
        return jsonify(alerts_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sustainability-metrics')
def get_sustainability_metrics():
    """Get sustainability metrics for dashboard"""
    try:
        biodiversity_service = BiodiversityService()
        metrics = biodiversity_service.calculate_sustainability_metrics()
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('base.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('base.html'), 500
