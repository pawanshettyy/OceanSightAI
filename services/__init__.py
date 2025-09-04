# services/__init__.py
"""
Services package for Marine Biodiversity Platform

This package contains service classes that handle business logic for:
- Ocean data processing and analysis
- Species identification and management  
- Fisheries data and sustainability metrics
- Biodiversity indices and ecosystem health
- OpenAI-powered species identification
"""

from .ocean_service import OceanService
from .species_service import SpeciesService  
from .fisheries_service import FisheriesService
from .biodiversity_service import BiodiversityService
from .openai_service import OpenAISpeciesIdentificationService

__all__ = [
    'OceanService',
    'SpeciesService', 
    'FisheriesService',
    'BiodiversityService',
    'OpenAISpeciesIdentificationService'
]