# Marine Biodiversity Platform

## Overview

The Marine Biodiversity Platform is a comprehensive web application for monitoring marine ecosystems, tracking biodiversity, and managing sustainable fisheries. The platform combines AI-powered species identification, real-time oceanographic data visualization, and environmental alert systems to support marine conservation efforts. Built with Flask and SQLAlchemy, it provides interactive dashboards, mapping capabilities, and data analytics for researchers, conservationists, and fisheries managers.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
The application follows a service-oriented architecture built on Flask with a modular design pattern. The core components include:

- **Flask Application**: Central application factory pattern with proxy middleware for deployment flexibility
- **Service Layer**: Dedicated service classes (OceanService, SpeciesService, FisheriesService, BiodiversityService) that handle business logic and data processing
- **Model Layer**: SQLAlchemy ORM models representing marine data entities (OceanData, Species, FisheriesData, BiodiversityIndex, Alert, SpeciesObservation)
- **Route Layer**: RESTful API endpoints and template rendering for both web interface and API consumption

### Database Design
The system uses SQLAlchemy with a flexible database configuration that defaults to SQLite for development but can be configured for other databases via environment variables. Key entities include:

- **OceanData**: Oceanographic measurements (temperature, salinity, pH, currents, depth)
- **Species**: Marine species catalog with conservation status and threat levels
- **FisheriesData**: Catch data with sustainability scoring and quota management
- **BiodiversityIndex**: Regional biodiversity assessments and ecosystem health metrics
- **Alert System**: Environmental monitoring alerts with severity classification

### Frontend Architecture
The frontend uses a template-based architecture with Bootstrap for responsive design and multiple JavaScript libraries for data visualization:

- **Template Engine**: Jinja2 templates with a base template inheritance pattern
- **UI Framework**: Bootstrap with custom CSS overrides for marine-themed styling
- **Mapping**: Leaflet.js for interactive oceanographic data visualization
- **Charts**: Chart.js for time series and statistical data presentation
- **Real-time Updates**: JavaScript-based periodic data refresh for dashboard metrics

### Data Processing Pipeline
The application implements a comprehensive data processing workflow:

- **Sample Data Initialization**: Automated database seeding with realistic marine biodiversity data
- **Real-time Analytics**: Service layer methods for calculating sustainability metrics and biodiversity indices
- **Geographic Filtering**: Location-based data queries for regional analysis
- **Temporal Analysis**: Time-range filtering for trend analysis and historical data comparison

## External Dependencies

### Core Web Framework
- **Flask**: Primary web application framework with CORS support for API access
- **SQLAlchemy**: ORM for database operations with connection pooling and migration support
- **Werkzeug**: WSGI utilities including ProxyFix for deployment behind reverse proxies

### Data Visualization
- **Chart.js**: Interactive charts for oceanographic data trends and species analytics
- **Leaflet.js**: Interactive mapping for geographic data visualization and ocean monitoring
- **Bootstrap**: Responsive UI framework with dark theme optimization for scientific applications

### Development and Deployment
- **Python Logging**: Comprehensive logging system for debugging and monitoring
- **Environment Configuration**: Flexible configuration management for database URLs and session secrets
- **Static Asset Management**: Organized CSS and JavaScript files for frontend functionality

### Optional Integrations
The architecture supports future integration of:
- **AI/ML Services**: For automated species identification from uploaded images
- **External Marine APIs**: For real-time oceanographic data feeds
- **Authentication Systems**: For user management and role-based access control
- **Cloud Storage**: For species image management and backup systems