// Marine Biodiversity Platform - Maps JavaScript
// Handles interactive map functionality for ocean data visualization

let oceanMap;
let currentMapLayers = {};
let mapMarkers = {};
let currentDataType = 'temperature';
let heatmapLayer;

// Initialize map when called
function initializeOceanMap() {
    if (oceanMap) {
        oceanMap.remove();
    }
    
    // Initialize the map centered on global ocean view
    oceanMap = L.map('ocean-map').setView([20, 0], 2);
    
    // Add base tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18
    }).addTo(oceanMap);
    
    // Load initial ocean data
    loadOceanDataForMap();
    
    // Set up map event listeners
    setupMapEventListeners();
    
    return oceanMap;
}

function setupMapEventListeners() {
    if (!oceanMap) return;
    
    // Map click event
    oceanMap.on('click', function(e) {
        const lat = e.latlng.lat.toFixed(4);
        const lng = e.latlng.lng.toFixed(4);
        
        // Show popup with coordinates and option to get detailed data
        const popup = L.popup()
            .setLatLng(e.latlng)
            .setContent(`
                <div>
                    <strong>Location:</strong><br>
                    Lat: ${lat}, Lng: ${lng}<br>
                    <button class="btn btn-sm btn-primary mt-2" onclick="getDetailedDataForLocation(${lat}, ${lng})">
                        <i class="fas fa-search me-1"></i>Get Ocean Data
                    </button>
                </div>
            `)
            .openOn(oceanMap);
    });
    
    // Map zoom event
    oceanMap.on('zoomend', function() {
        updateMapMarkersVisibility();
    });
}

function loadOceanDataForMap() {
    fetch('/api/ocean-data')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            displayOceanDataOnMap(data);
        })
        .catch(error => {
            console.error('Error loading ocean data for map:', error);
            showMapError('Failed to load ocean data');
        });
}

function displayOceanDataOnMap(data) {
    if (!oceanMap || !data) return;
    
    // Clear existing layers
    clearMapLayers();
    
    // Display data based on current type
    switch (currentDataType) {
        case 'temperature':
            displayTemperatureData(data.temperature_data);
            break;
        case 'salinity':
            displaySalinityData(data.salinity_data);
            break;
        case 'currents':
            displayCurrentData(data.current_data);
            break;
        case 'ph':
            displayPHData(data.ph_data);
            break;
    }
    
    // Add marine protected areas
    addMarineProtectedAreas();
}

function displayTemperatureData(temperatureData) {
    if (!temperatureData || temperatureData.length === 0) {
        showMapMessage('No temperature data available');
        return;
    }
    
    // Create heat map points
    const heatmapPoints = temperatureData.map(point => [
        point.lat,
        point.lng,
        Math.max(0, Math.min(1, (point.value - 0) / 35)) // Normalize temperature to 0-1
    ]);
    
    // Add heatmap layer if available
    if (L.heatLayer) {
        if (heatmapLayer) {
            oceanMap.removeLayer(heatmapLayer);
        }
        
        heatmapLayer = L.heatLayer(heatmapPoints, {
            radius: 25,
            blur: 15,
            maxZoom: 17,
            gradient: {
                0.0: 'blue',
                0.3: 'cyan',
                0.5: 'lime',
                0.7: 'yellow',
                1.0: 'red'
            }
        }).addTo(oceanMap);
    } else {
        // Fallback to circle markers
        temperatureData.forEach(point => {
            const marker = L.circleMarker([point.lat, point.lng], {
                radius: 8,
                fillColor: getTemperatureColor(point.value),
                color: '#fff',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.8
            }).addTo(oceanMap);
            
            marker.bindPopup(`
                <div>
                    <strong>Temperature Data</strong><br>
                    Temperature: ${point.value.toFixed(1)}°C<br>
                    Location: ${point.location || 'Unknown'}<br>
                    Time: ${formatDate(point.timestamp)}
                </div>
            `);
            
            mapMarkers.temperature = mapMarkers.temperature || [];
            mapMarkers.temperature.push(marker);
        });
    }
}

function displaySalinityData(salinityData) {
    if (!salinityData || salinityData.length === 0) {
        showMapMessage('No salinity data available');
        return;
    }
    
    salinityData.forEach(point => {
        const marker = L.circleMarker([point.lat, point.lng], {
            radius: 6,
            fillColor: getSalinityColor(point.value),
            color: '#fff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        }).addTo(oceanMap);
        
        marker.bindPopup(`
            <div>
                <strong>Salinity Data</strong><br>
                Salinity: ${point.value.toFixed(1)}‰<br>
                Location: ${point.location || 'Unknown'}<br>
                Time: ${formatDate(point.timestamp)}
            </div>
        `);
        
        mapMarkers.salinity = mapMarkers.salinity || [];
        mapMarkers.salinity.push(marker);
    });
}

function displayCurrentData(currentData) {
    if (!currentData || currentData.length === 0) {
        showMapMessage('No current data available');
        return;
    }
    
    currentData.forEach(point => {
        // Create arrow for current direction
        const arrowIcon = createCurrentArrow(point.direction, point.speed);
        
        const marker = L.marker([point.lat, point.lng], {
            icon: arrowIcon
        }).addTo(oceanMap);
        
        marker.bindPopup(`
            <div>
                <strong>Ocean Current</strong><br>
                Speed: ${point.speed.toFixed(2)} m/s<br>
                Direction: ${point.direction.toFixed(0)}°<br>
                Time: ${formatDate(point.timestamp)}
            </div>
        `);
        
        mapMarkers.currents = mapMarkers.currents || [];
        mapMarkers.currents.push(marker);
    });
}

function displayPHData(phData) {
    if (!phData || phData.length === 0) {
        showMapMessage('No pH data available');
        return;
    }
    
    phData.forEach(point => {
        const marker = L.circleMarker([point.lat, point.lng], {
            radius: 6,
            fillColor: getPHColor(point.value),
            color: '#fff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        }).addTo(oceanMap);
        
        marker.bindPopup(`
            <div>
                <strong>pH Level</strong><br>
                pH: ${point.value.toFixed(2)}<br>
                Location: ${point.location || 'Unknown'}<br>
                Time: ${formatDate(point.timestamp)}
            </div>
        `);
        
        mapMarkers.ph = mapMarkers.ph || [];
        mapMarkers.ph.push(marker);
    });
}

function addMarineProtectedAreas() {
    // Mock marine protected areas data - in real implementation, this would come from an API
    const protectedAreas = [
        { lat: 25.7, lng: -80.2, name: "Florida Keys National Marine Sanctuary", size: "large" },
        { lat: 42.0, lng: -70.0, name: "Stellwagen Bank National Marine Sanctuary", size: "medium" },
        { lat: 37.8, lng: -122.5, name: "Gulf of the Farallones National Marine Sanctuary", size: "large" },
        { lat: -25.3, lng: 153.1, name: "Great Barrier Reef Marine Park", size: "large" },
        { lat: 60.0, lng: 5.0, name: "Nordic Marine Protected Area", size: "medium" }
    ];
    
    protectedAreas.forEach(area => {
        const circle = L.circle([area.lat, area.lng], {
            color: '#28a745',
            fillColor: '#28a745',
            fillOpacity: 0.2,
            radius: area.size === 'large' ? 50000 : 25000
        }).addTo(oceanMap);
        
        circle.bindPopup(`
            <div>
                <strong>${area.name}</strong><br>
                <span class="badge bg-success">Marine Protected Area</span><br>
                Size: ${area.size.charAt(0).toUpperCase() + area.size.slice(1)}
            </div>
        `);
        
        mapMarkers.protected = mapMarkers.protected || [];
        mapMarkers.protected.push(circle);
    });
}

function updateMapDataType(dataType) {
    currentDataType = dataType;
    loadOceanDataForMap();
}

function clearMapLayers() {
    // Remove heatmap layer
    if (heatmapLayer) {
        oceanMap.removeLayer(heatmapLayer);
        heatmapLayer = null;
    }
    
    // Remove all markers except protected areas
    Object.keys(mapMarkers).forEach(type => {
        if (type !== 'protected' && mapMarkers[type]) {
            mapMarkers[type].forEach(marker => {
                oceanMap.removeLayer(marker);
            });
            mapMarkers[type] = [];
        }
    });
}

function updateMapMarkersVisibility() {
    const zoom = oceanMap.getZoom();
    
    // Hide/show markers based on zoom level
    Object.keys(mapMarkers).forEach(type => {
        if (mapMarkers[type]) {
            mapMarkers[type].forEach(marker => {
                if (zoom < 4 && type !== 'protected') {
                    marker.setStyle({ opacity: 0.3, fillOpacity: 0.3 });
                } else {
                    marker.setStyle({ opacity: 1, fillOpacity: 0.8 });
                }
            });
        }
    });
}

function getDetailedDataForLocation(lat, lng) {
    // This would fetch detailed data for a specific location
    const popup = L.popup()
        .setLatLng([lat, lng])
        .setContent(`
            <div class="text-center">
                <i class="fas fa-spinner fa-spin"></i><br>
                Loading detailed data...
            </div>
        `)
        .openOn(oceanMap);
    
    // Mock detailed data - in real implementation, this would be an API call
    setTimeout(() => {
        popup.setContent(`
            <div>
                <strong>Ocean Data Summary</strong><br>
                <small>Lat: ${lat}, Lng: ${lng}</small><br><br>
                <strong>Temperature:</strong> 22.5°C<br>
                <strong>Salinity:</strong> 35.2‰<br>
                <strong>pH:</strong> 8.1<br>
                <strong>Depth:</strong> 1,200m<br>
                <hr>
                <small class="text-muted">
                    Data from latest measurements
                </small>
            </div>
        `);
    }, 1000);
}

// Color functions for different data types
function getTemperatureColor(temp) {
    if (temp < 5) return '#000080';
    if (temp < 10) return '#0000ff';
    if (temp < 15) return '#00ffff';
    if (temp < 20) return '#00ff00';
    if (temp < 25) return '#ffff00';
    if (temp < 30) return '#ff8000';
    return '#ff0000';
}

function getSalinityColor(salinity) {
    if (salinity < 30) return '#ff0000';
    if (salinity < 32) return '#ff8000';
    if (salinity < 35) return '#ffff00';
    if (salinity < 37) return '#00ff00';
    if (salinity < 40) return '#0080ff';
    return '#0000ff';
}

function getPHColor(ph) {
    if (ph < 7.0) return '#ff0000';
    if (ph < 7.5) return '#ff8000';
    if (ph < 8.0) return '#ffff00';
    if (ph < 8.3) return '#00ff00';
    if (ph < 8.5) return '#0080ff';
    return '#8000ff';
}

function createCurrentArrow(direction, speed) {
    // Create a simple arrow icon pointing in the current direction
    const size = Math.min(20, Math.max(8, speed * 2));
    
    return L.divIcon({
        html: `<div style="
            width: ${size}px; 
            height: ${size}px; 
            transform: rotate(${direction}deg);
            color: #0080ff;
            font-size: ${size}px;
            line-height: 1;
            text-align: center;
        ">↑</div>`,
        iconSize: [size, size],
        iconAnchor: [size/2, size/2],
        className: 'current-arrow-icon'
    });
}

function showMapError(message) {
    if (!oceanMap) return;
    
    const errorControl = L.control({ position: 'topright' });
    errorControl.onAdd = function() {
        const div = L.DomUtil.create('div', 'map-error-message');
        div.innerHTML = `
            <div class="alert alert-danger alert-sm">
                <i class="fas fa-exclamation-triangle me-1"></i>
                ${message}
            </div>
        `;
        return div;
    };
    errorControl.addTo(oceanMap);
    
    // Remove error message after 5 seconds
    setTimeout(() => {
        if (errorControl) {
            oceanMap.removeControl(errorControl);
        }
    }, 5000);
}

function showMapMessage(message) {
    if (!oceanMap) return;
    
    const messageControl = L.control({ position: 'topright' });
    messageControl.onAdd = function() {
        const div = L.DomUtil.create('div', 'map-info-message');
        div.innerHTML = `
            <div class="alert alert-info alert-sm">
                <i class="fas fa-info-circle me-1"></i>
                ${message}
            </div>
        `;
        return div;
    };
    messageControl.addTo(oceanMap);
    
    // Remove message after 3 seconds
    setTimeout(() => {
        if (messageControl) {
            oceanMap.removeControl(messageControl);
        }
    }, 3000);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleString();
}

// Export functions for global access
window.initializeOceanMap = initializeOceanMap;
window.updateMapDataType = updateMapDataType;
window.getDetailedDataForLocation = getDetailedDataForLocation;
