# services/ocean_service.py
from app import db, OceanData
from datetime import datetime, timedelta

class OceanService:
    def get_ocean_data_for_region(self, lat_min=None, lat_max=None, lng_min=None, lng_max=None):
        """Get oceanographic data for a specific region"""
        query = OceanData.query
        
        if lat_min is not None:
            query = query.filter(OceanData.latitude >= lat_min)
        if lat_max is not None:
            query = query.filter(OceanData.latitude <= lat_max)
        if lng_min is not None:
            query = query.filter(OceanData.longitude >= lng_min)
        if lng_max is not None:
            query = query.filter(OceanData.longitude <= lng_max)
        
        # Get recent data (last 30 days) and limit results for performance
        recent_date = datetime.utcnow() - timedelta(days=30)
        data = query.filter(OceanData.timestamp >= recent_date)\
                   .order_by(OceanData.timestamp.desc())\
                   .limit(1000).all()
        
        return [{
            'id': point.id,
            'latitude': point.latitude,
            'longitude': point.longitude,
            'temperature': point.temperature,
            'salinity': point.salinity,
            'ph_level': point.ph_level,
            'oxygen_level': point.oxygen_level,
            'current_speed': point.current_speed,
            'current_direction': point.current_direction,
            'depth': point.depth,
            'timestamp': point.timestamp.isoformat() if point.timestamp else None,
            'location_name': point.location_name
        } for point in data]
    
    def get_temperature_trends(self, days=30):
        """Get temperature trend data for charts"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        data = db.session.query(OceanData)\
                        .filter(OceanData.timestamp >= start_date)\
                        .filter(OceanData.temperature.isnot(None))\
                        .order_by(OceanData.timestamp)\
                        .all()
        
        return [{
            'date': point.timestamp.strftime('%Y-%m-%d'),
            'temperature': point.temperature,
            'location': point.location_name
        } for point in data]
    
    def get_current_conditions(self):
        """Get latest oceanographic conditions"""
        latest_data = OceanData.query\
                               .order_by(OceanData.timestamp.desc())\
                               .limit(10).all()
        
        if not latest_data:
            return {
                'avg_temperature': 0,
                'avg_salinity': 0,
                'avg_ph': 0,
                'data_points': 0
            }
        
        avg_temp = sum(p.temperature for p in latest_data if p.temperature) / len([p for p in latest_data if p.temperature])
        avg_salinity = sum(p.salinity for p in latest_data if p.salinity) / len([p for p in latest_data if p.salinity])
        avg_ph = sum(p.ph_level for p in latest_data if p.ph_level) / len([p for p in latest_data if p.ph_level])
        
        return {
            'avg_temperature': round(avg_temp, 2),
            'avg_salinity': round(avg_salinity, 2),
            'avg_ph': round(avg_ph, 2),
            'data_points': len(latest_data)
        }