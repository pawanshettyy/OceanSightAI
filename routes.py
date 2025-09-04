from flask import render_template, request, jsonify, redirect, url_for, flash
from app import app, db
from app import OceanData, Species, FisheriesData, BiodiversityIndex, Alert, SpeciesObservation, db
from services.ocean_service import OceanService
from services.species_service import SpeciesService
from services.fisheries_service import FisheriesService
from services.biodiversity_service import BiodiversityService
from services.openai_service import OpenAISpeciesIdentificationService
from datetime import datetime, timedelta
import json
import base64
import os

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
    """Real species identification using OpenAI Vision API"""
    try:
        # Check if OpenAI API key is available
        if not os.environ.get("OPENAI_API_KEY"):
            # Fall back to mock identification if no API key
            species_service = SpeciesService()
            result = species_service.mock_species_identification()
            result['note'] = 'Using mock identification - OpenAI API key not configured'
            return jsonify(result)
        
        # Get image data from request
        if 'file' in request.files:
            # File upload
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            image_data = file.read()
        elif request.json and 'image_data' in request.json:
            # Base64 encoded image data
            image_data = request.json['image_data']
        else:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Get location context if provided
        location = request.json.get('location', 'Indian Ocean') if request.json else 'Indian Ocean'
        
        # Initialize OpenAI service and identify species
        openai_service = OpenAISpeciesIdentificationService()
        result = openai_service.identify_marine_species(image_data, location)
        
        # If successfully identified, try to find or create species in database
        if result.get('identified') and result.get('scientific_name'):
            species_service = SpeciesService()
            species_id = species_service.find_or_create_species({
                'scientific_name': result['scientific_name'],
                'common_name': result['common_name'],
                'species_type': result.get('species_type', 'unknown'),
                'conservation_status': result.get('conservation_status', 'unknown'),
                'threat_level': result.get('threat_level', 'unknown'),
                'habitat': result.get('habitat', ''),
                'description': result.get('description', '')
            })
            result['species_id'] = species_id
        
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Species identification error: {str(e)}")
        return jsonify({
            'identified': False,
            'error': f'Error during species identification: {str(e)}',
            'confidence': 0
        }), 500

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
