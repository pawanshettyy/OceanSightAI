# services/fisheries_service.py
from app import db, FisheriesData, Species
from datetime import datetime, timedelta
from sqlalchemy import func

class FisheriesService:
    def get_catch_data(self, start_date=None, end_date=None):
        """Get fisheries catch data for a date range"""
        query = db.session.query(FisheriesData, Species)\
                          .join(Species, FisheriesData.species_id == Species.id)
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                query = query.filter(FisheriesData.catch_date >= start_dt)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                query = query.filter(FisheriesData.catch_date <= end_dt)
            except ValueError:
                pass
        
        # Default to last 90 days if no dates provided
        if not start_date and not end_date:
            recent_date = datetime.utcnow() - timedelta(days=90)
            query = query.filter(FisheriesData.catch_date >= recent_date)
        
        results = query.order_by(FisheriesData.catch_date.desc()).limit(500).all()
        
        catch_data = []
        for fisheries, species in results:
            catch_data.append({
                'id': fisheries.id,
                'species_name': species.common_name or species.scientific_name,
                'scientific_name': species.scientific_name,
                'catch_amount': fisheries.catch_amount,
                'fishing_area': fisheries.fishing_area,
                'latitude': fisheries.latitude,
                'longitude': fisheries.longitude,
                'fishing_method': fisheries.fishing_method,
                'vessel_type': fisheries.vessel_type,
                'catch_date': fisheries.catch_date.isoformat() if fisheries.catch_date else None,
                'quota_limit': fisheries.quota_limit,
                'sustainability_score': fisheries.sustainability_score,
                'conservation_status': species.conservation_status,
                'threat_level': species.threat_level
            })
        
        return catch_data
    
    def get_sustainability_summary(self):
        """Get sustainability metrics summary"""
        # Calculate average sustainability score
        avg_score = db.session.query(func.avg(FisheriesData.sustainability_score))\
                             .filter(FisheriesData.sustainability_score.isnot(None))\
                             .scalar() or 0
        
        # Count quota violations
        quota_violations = db.session.query(FisheriesData)\
                                    .filter(FisheriesData.catch_amount > FisheriesData.quota_limit)\
                                    .count()
        
        # Total catch in last 30 days
        recent_date = datetime.utcnow() - timedelta(days=30)
        recent_catch = db.session.query(func.sum(FisheriesData.catch_amount))\
                                .filter(FisheriesData.catch_date >= recent_date)\
                                .scalar() or 0
        
        # Species at risk (high/critical threat level)
        at_risk_species = db.session.query(Species)\
                                   .filter(Species.threat_level.in_(['high', 'critical']))\
                                   .count()
        
        return {
            'avg_sustainability_score': round(avg_score, 1),
            'quota_violations': quota_violations,
            'recent_catch_total': round(recent_catch, 1),
            'at_risk_species_count': at_risk_species
        }
    
    def get_catch_by_species(self):
        """Get catch totals by species for charts"""
        results = db.session.query(
            Species.common_name,
            Species.scientific_name,
            func.sum(FisheriesData.catch_amount).label('total_catch'),
            func.avg(FisheriesData.sustainability_score).label('avg_sustainability')
        ).join(FisheriesData, Species.id == FisheriesData.species_id)\
         .group_by(Species.id, Species.common_name, Species.scientific_name)\
         .order_by(func.sum(FisheriesData.catch_amount).desc())\
         .limit(15).all()
        
        return [{
            'species_name': result.common_name or result.scientific_name,
            'total_catch': float(result.total_catch or 0),
            'avg_sustainability': float(result.avg_sustainability or 0)
        } for result in results]