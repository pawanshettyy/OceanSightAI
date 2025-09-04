// Marine Biodiversity Platform - Species JavaScript
// Handles species identification and database functionality

let speciesDatabase = [];
let filteredSpecies = [];
let speciesMap;
let uploadedImageFile = null;
let cameraStream = null;
let captureMode = 'upload';

// Initialize species page
function initializeSpeciesPage() {
    setupImageUpload();
    setupCameraControls();
    loadSpeciesDatabase();
    initializeSpeciesMap();
    setupEventListeners();
    loadThreatenedSpeciesSummary();
}

function setupImageUpload() {
    const uploadArea = document.getElementById('image-upload-area');
    const fileInput = document.getElementById('species-image');
    const identifyBtn = document.getElementById('identify-btn');
    
    if (!uploadArea || !fileInput || !identifyBtn) return;
    
    // Click to upload
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });
    
    // Drag and drop functionality
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleImageUpload(files[0]);
        }
    });
    
    // File input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleImageUpload(e.target.files[0]);
        }
    });
    
    // Identify button click
    identifyBtn.addEventListener('click', performSpeciesIdentification);
}

function setupCameraControls() {
    const uploadModeBtn = document.getElementById('upload-mode');
    const cameraModeBtn = document.getElementById('camera-mode');
    const uploadSection = document.getElementById('upload-section');
    const cameraSection = document.getElementById('camera-section');
    const startCameraBtn = document.getElementById('start-camera-btn');
    const capturePhotoBtn = document.getElementById('capture-photo-btn');
    const stopCameraBtn = document.getElementById('stop-camera-btn');
    const retakeBtn = document.getElementById('retake-btn');
    
    if (!uploadModeBtn || !cameraModeBtn) return;
    
    // Mode toggle listeners
    uploadModeBtn.addEventListener('change', () => {
        if (uploadModeBtn.checked) {
            captureMode = 'upload';
            uploadSection.classList.remove('d-none');
            cameraSection.classList.add('d-none');
            stopCamera();
        }
    });
    
    cameraModeBtn.addEventListener('change', () => {
        if (cameraModeBtn.checked) {
            captureMode = 'camera';
            uploadSection.classList.add('d-none');
            cameraSection.classList.remove('d-none');
        }
    });
    
    // Camera control listeners
    if (startCameraBtn) {
        startCameraBtn.addEventListener('click', startCamera);
    }
    
    if (capturePhotoBtn) {
        capturePhotoBtn.addEventListener('click', capturePhoto);
    }
    
    if (stopCameraBtn) {
        stopCameraBtn.addEventListener('click', stopCamera);
    }
    
    if (retakeBtn) {
        retakeBtn.addEventListener('click', retakePhoto);
    }
}

async function startCamera() {
    try {
        const video = document.getElementById('camera-video');
        const startBtn = document.getElementById('start-camera-btn');
        const captureBtn = document.getElementById('capture-photo-btn');
        const stopBtn = document.getElementById('stop-camera-btn');
        
        if (!video) return;
        
        // Request camera access
        cameraStream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: 'environment' // Use rear camera if available
            },
            audio: false
        });
        
        video.srcObject = cameraStream;
        video.play();
        
        // Update button states
        startBtn.classList.add('d-none');
        captureBtn.classList.remove('d-none');
        stopBtn.classList.remove('d-none');
        
        // Hide any previous captured image
        const imageContainer = document.getElementById('uploaded-image-container');
        if (imageContainer) {
            imageContainer.classList.add('d-none');
        }
        
        // Reset identify button
        const identifyBtn = document.getElementById('identify-btn');
        if (identifyBtn) {
            identifyBtn.disabled = true;
            identifyBtn.innerHTML = '<i class="fas fa-search me-2"></i>Identify Species with AI';
        }
        
    } catch (error) {
        console.error('Error accessing camera:', error);
        showError('Unable to access camera. Please check your camera permissions and try again.');
    }
}

function capturePhoto() {
    const video = document.getElementById('camera-video');
    const canvas = document.getElementById('camera-canvas');
    const imageContainer = document.getElementById('uploaded-image-container');
    const image = document.getElementById('uploaded-image');
    const identifyBtn = document.getElementById('identify-btn');
    
    if (!video || !canvas || !imageContainer || !image) return;
    
    const context = canvas.getContext('2d');
    
    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Draw the current video frame to canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Convert canvas to blob
    canvas.toBlob((blob) => {
        uploadedImageFile = blob;
        
        // Display captured image
        const imageUrl = URL.createObjectURL(blob);
        image.src = imageUrl;
        imageContainer.classList.remove('d-none');
        
        // Enable identify button
        if (identifyBtn) {
            identifyBtn.disabled = false;
        }
        
        // Hide video feed
        video.style.display = 'none';
        
        // Update button states
        const captureBtn = document.getElementById('capture-photo-btn');
        const stopBtn = document.getElementById('stop-camera-btn');
        if (captureBtn) captureBtn.classList.add('d-none');
        if (stopBtn) stopBtn.classList.add('d-none');
        
    }, 'image/jpeg', 0.8);
}

function retakePhoto() {
    const video = document.getElementById('camera-video');
    const imageContainer = document.getElementById('uploaded-image-container');
    const identifyBtn = document.getElementById('identify-btn');
    
    // Hide captured image
    if (imageContainer) {
        imageContainer.classList.add('d-none');
    }
    
    // Show video feed again
    if (video) {
        video.style.display = 'block';
    }
    
    // Update button states
    const captureBtn = document.getElementById('capture-photo-btn');
    const stopBtn = document.getElementById('stop-camera-btn');
    if (captureBtn) captureBtn.classList.remove('d-none');
    if (stopBtn) stopBtn.classList.remove('d-none');
    
    // Disable identify button
    if (identifyBtn) {
        identifyBtn.disabled = true;
    }
    
    uploadedImageFile = null;
}

function stopCamera() {
    const video = document.getElementById('camera-video');
    const startBtn = document.getElementById('start-camera-btn');
    const captureBtn = document.getElementById('capture-photo-btn');
    const stopBtn = document.getElementById('stop-camera-btn');
    
    if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
        cameraStream = null;
    }
    
    if (video) {
        video.srcObject = null;
        video.style.display = 'block';
    }
    
    // Reset button states
    if (startBtn) startBtn.classList.remove('d-none');
    if (captureBtn) captureBtn.classList.add('d-none');
    if (stopBtn) stopBtn.classList.add('d-none');
    
    // Hide captured image
    const imageContainer = document.getElementById('uploaded-image-container');
    if (imageContainer) {
        imageContainer.classList.add('d-none');
    }
    
    // Reset identify button
    const identifyBtn = document.getElementById('identify-btn');
    if (identifyBtn) {
        identifyBtn.disabled = true;
        identifyBtn.innerHTML = '<i class="fas fa-search me-2"></i>Identify Species with AI';
    }
    
    uploadedImageFile = null;
}

function handleImageUpload(file) {
    if (!file.type.startsWith('image/')) {
        showError('Please upload a valid image file');
        return;
    }
    
    if (file.size > 10 * 1024 * 1024) { // 10MB limit
        showError('File size must be less than 10MB');
        return;
    }
    
    uploadedImageFile = file;
    
    // Display uploaded image
    const reader = new FileReader();
    reader.onload = function(e) {
        const imageContainer = document.getElementById('uploaded-image-container');
        const image = document.getElementById('uploaded-image');
        
        if (imageContainer && image) {
            image.src = e.target.result;
            imageContainer.classList.remove('d-none');
        }
        
        // Enable identify button
        const identifyBtn = document.getElementById('identify-btn');
        if (identifyBtn) {
            identifyBtn.disabled = false;
        }
    };
    
    reader.readAsDataURL(file);
}

function performSpeciesIdentification() {
    if (!uploadedImageFile) {
        showError('Please upload or capture an image first');
        return;
    }
    
    const resultsContainer = document.getElementById('identification-results');
    const identifyBtn = document.getElementById('identify-btn');
    
    if (!resultsContainer) return;
    
    // Show loading state
    resultsContainer.innerHTML = `
        <div class="text-center">
            <div class="loading-modern">
                <div class="spinner-modern"></div>
                <span>AI is analyzing the marine species...</span>
            </div>
            <p class="mt-2">This may take a few moments for accurate identification</p>
        </div>
    `;
    
    if (identifyBtn) {
        identifyBtn.disabled = true;
        identifyBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Analyzing with AI...';
    }
    
    // Prepare FormData to send image file
    const formData = new FormData();
    formData.append('file', uploadedImageFile);
    
    // Call identification API with real image data
    fetch('/api/species/identify', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(result => {
        displayIdentificationResult(result);
    })
    .catch(error => {
        console.error('Error identifying species:', error);
        resultsContainer.innerHTML = `
            <div class="alert alert-modern alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                <strong>Identification Failed</strong><br>
                Error occurred during species identification. Please check your internet connection and try again.
            </div>
        `;
    })
    .finally(() => {
        if (identifyBtn) {
            identifyBtn.disabled = false;
            identifyBtn.innerHTML = '<i class="fas fa-search me-2"></i>Identify Species with AI';
        }
    });
}

function displayIdentificationResult(result) {
    const resultsContainer = document.getElementById('identification-results');
    if (!resultsContainer) return;
    
    if (!result.identified) {
        resultsContainer.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-question-circle me-2"></i>
                <strong>Species Not Identified</strong><br>
                ${result.error || 'Unable to identify the species from this image. Please try with a clearer image or different angle.'}
            </div>
        `;
        return;
    }
    
    const confidenceColor = getConfidenceColor(result.confidence);
    const threatColor = getThreatLevelColor(result.threat_level);
    
    resultsContainer.innerHTML = `
        <div class="identification-result">
            <div class="row">
                <div class="col-12">
                    <div class="alert alert-success">
                        <h6 class="alert-heading">
                            <i class="fas fa-check-circle me-2"></i>
                            Species Identified!
                        </h6>
                        
                        <div class="mb-3">
                            <strong>Scientific Name:</strong> <em>${result.scientific_name}</em><br>
                            <strong>Common Name:</strong> ${result.common_name}
                        </div>
                        
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <strong>Confidence Level:</strong>
                                <div class="progress mt-1" style="height: 20px;">
                                    <div class="progress-bar bg-${confidenceColor}" 
                                         style="width: ${result.confidence}%">
                                        ${result.confidence.toFixed(1)}%
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <strong>Conservation Status:</strong><br>
                                <span class="badge bg-${getConservationStatusColor(result.conservation_status)}">
                                    ${result.conservation_status}
                                </span>
                                <span class="badge bg-${threatColor} ms-2">
                                    ${result.threat_level} Risk
                                </span>
                            </div>
                        </div>
                        
                        ${result.description ? `
                            <div class="mb-3">
                                <strong>Description:</strong><br>
                                <p class="mb-2">${result.description}</p>
                            </div>
                        ` : ''}
                        
                        ${result.recommendations ? `
                            <div class="mb-3">
                                <strong>Conservation Recommendations:</strong>
                                <ul class="mb-0">
                                    ${result.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                                </ul>
                            </div>
                        ` : ''}
                        
                        <div class="d-flex gap-2 mt-3">
                            <button class="btn btn-outline-primary btn-sm" onclick="viewSpeciesDetails(${result.species_id})">
                                <i class="fas fa-info-circle me-1"></i>View Details
                            </button>
                            <button class="btn btn-outline-success btn-sm" onclick="reportObservation(${result.species_id})">
                                <i class="fas fa-map-marker-alt me-1"></i>Report Observation
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function loadSpeciesDatabase() {
    fetch('/api/species-data')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            speciesDatabase = data;
            filteredSpecies = data;
            displaySpeciesList(data);
        })
        .catch(error => {
            console.error('Error loading species database:', error);
            displaySpeciesError('Failed to load species database');
        });
}

function displaySpeciesList(species) {
    const container = document.getElementById('species-list');
    if (!container) return;
    
    if (species.length === 0) {
        container.innerHTML = `
            <div class="col-12 text-center py-4">
                <i class="fas fa-search fa-3x text-muted mb-3"></i>
                <h5>No species found</h5>
                <p class="text-muted">Try adjusting your search filters</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = species.map(spec => `
        <div class="col-lg-4 col-md-6 mb-4">
            <div class="card species-card h-100" onclick="viewSpeciesDetails(${spec.id})">
                <div class="card-body">
                    <h6 class="card-title">
                        <em>${spec.scientific_name}</em>
                    </h6>
                    <p class="card-text">
                        <strong>${spec.common_name}</strong><br>
                        <small class="text-muted">${spec.species_type}</small>
                    </p>
                    
                    <div class="mb-2">
                        <span class="badge bg-${getConservationStatusColor(spec.conservation_status)}">
                            ${spec.conservation_status || 'Unknown'}
                        </span>
                        <span class="badge bg-${getThreatLevelColor(spec.threat_level)} ms-1">
                            ${spec.threat_level || 'Unknown'} Risk
                        </span>
                    </div>
                    
                    <div class="mb-2">
                        <small>
                            <i class="fas fa-eye me-1"></i>
                            ${spec.recent_observations} recent observations
                        </small>
                    </div>
                    
                    ${spec.population_trend ? `
                        <div class="mb-2">
                            <small>
                                <i class="fas fa-chart-line me-1"></i>
                                Population: ${spec.population_trend}
                            </small>
                        </div>
                    ` : ''}
                    
                    ${spec.habitat ? `
                        <div>
                            <small class="text-muted">
                                <i class="fas fa-home me-1"></i>
                                ${spec.habitat}
                            </small>
                        </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `).join('');
}

function setupEventListeners() {
    // Species filter
    const speciesFilter = document.getElementById('species-filter');
    const statusFilter = document.getElementById('status-filter');
    const searchInput = document.getElementById('species-search');
    
    if (speciesFilter) {
        speciesFilter.addEventListener('change', applyFilters);
    }
    
    if (statusFilter) {
        statusFilter.addEventListener('change', applyFilters);
    }
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce(applyFilters, 300));
    }
}

function applyFilters() {
    const speciesType = document.getElementById('species-filter')?.value || '';
    const conservationStatus = document.getElementById('status-filter')?.value || '';
    const searchTerm = document.getElementById('species-search')?.value.toLowerCase() || '';
    
    filteredSpecies = speciesDatabase.filter(species => {
        // Filter by species type
        if (speciesType && species.species_type !== speciesType) {
            return false;
        }
        
        // Filter by conservation status
        if (conservationStatus && species.conservation_status !== conservationStatus) {
            return false;
        }
        
        // Filter by search term
        if (searchTerm) {
            const searchableText = `
                ${species.scientific_name} 
                ${species.common_name} 
                ${species.description || ''}
            `.toLowerCase();
            
            if (!searchableText.includes(searchTerm)) {
                return false;
            }
        }
        
        return true;
    });
    
    displaySpeciesList(filteredSpecies);
}

function initializeSpeciesMap() {
    if (typeof L === 'undefined') {
        console.error('Leaflet library not loaded');
        return;
    }
    
    speciesMap = L.map('species-map').setView([20, 0], 2);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(speciesMap);
    
    // Load species observations
    loadSpeciesObservations();
}

function loadSpeciesObservations() {
    // Mock species observations - in real implementation, this would come from API
    const observations = [
        { lat: 25.7, lng: -80.2, species: 'Atlantic Bluefin Tuna', threat_level: 'critical', count: 5 },
        { lat: 42.0, lng: -70.0, species: 'North Atlantic Right Whale', threat_level: 'critical', count: 2 },
        { lat: 37.8, lng: -122.5, species: 'Great White Shark', threat_level: 'vulnerable', count: 8 },
        { lat: -25.3, lng: 153.1, species: 'Green Sea Turtle', threat_level: 'endangered', count: 12 },
        { lat: 60.0, lng: 5.0, species: 'Atlantic Cod', threat_level: 'vulnerable', count: 15 }
    ];
    
    observations.forEach(obs => {
        const color = getThreatLevelMapColor(obs.threat_level);
        const radius = Math.min(20, Math.max(8, obs.count * 1.5));
        
        const marker = L.circleMarker([obs.lat, obs.lng], {
            radius: radius,
            fillColor: color,
            color: '#fff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        }).addTo(speciesMap);
        
        marker.bindPopup(`
            <div>
                <strong>${obs.species}</strong><br>
                Observations: ${obs.count}<br>
                Threat Level: <span class="badge bg-${getThreatLevelColor(obs.threat_level)}">${obs.threat_level}</span>
            </div>
        `);
    });
}

function loadThreatenedSpeciesSummary() {
    const container = document.getElementById('threatened-species-summary');
    if (!container) return;
    
    // Mock threatened species data - in real implementation, this would come from API
    const summary = {
        total_threatened: 45,
        critical: 12,
        high_risk: 18,
        medium_risk: 15,
        recent_alerts: 3
    };
    
    container.innerHTML = `
        <div class="row">
            <div class="col-md-8">
                <div class="row">
                    <div class="col-sm-3">
                        <div class="text-center">
                            <div class="h4 text-danger">${summary.critical}</div>
                            <small>Critical</small>
                        </div>
                    </div>
                    <div class="col-sm-3">
                        <div class="text-center">
                            <div class="h4 text-warning">${summary.high_risk}</div>
                            <small>High Risk</small>
                        </div>
                    </div>
                    <div class="col-sm-3">
                        <div class="text-center">
                            <div class="h4 text-info">${summary.medium_risk}</div>
                            <small>Medium Risk</small>
                        </div>
                    </div>
                    <div class="col-sm-3">
                        <div class="text-center">
                            <div class="h4 text-primary">${summary.total_threatened}</div>
                            <small>Total Threatened</small>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="alert alert-warning mb-0">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <strong>${summary.recent_alerts} new alerts</strong> in the past 24 hours
                </div>
            </div>
        </div>
    `;
}

function viewSpeciesDetails(speciesId) {
    const species = speciesDatabase.find(s => s.id === speciesId);
    if (!species) {
        showError('Species not found');
        return;
    }
    
    const modal = new bootstrap.Modal(document.getElementById('speciesModal'));
    const modalTitle = document.getElementById('speciesModalTitle');
    const modalBody = document.getElementById('speciesModalBody');
    
    if (modalTitle) {
        modalTitle.textContent = species.common_name;
    }
    
    if (modalBody) {
        modalBody.innerHTML = `
            <div class="row">
                <div class="col-12">
                    <h6><em>${species.scientific_name}</em></h6>
                    
                    <div class="row mb-3">
                        <div class="col-md-6">
                            <strong>Type:</strong> ${species.species_type}<br>
                            <strong>Conservation Status:</strong> 
                            <span class="badge bg-${getConservationStatusColor(species.conservation_status)}">
                                ${species.conservation_status}
                            </span><br>
                            <strong>Threat Level:</strong> 
                            <span class="badge bg-${getThreatLevelColor(species.threat_level)}">
                                ${species.threat_level}
                            </span>
                        </div>
                        <div class="col-md-6">
                            <strong>Population Trend:</strong> ${species.population_trend || 'Unknown'}<br>
                            <strong>Recent Observations:</strong> ${species.recent_observations}<br>
                            <strong>Habitat:</strong> ${species.habitat || 'Unknown'}
                        </div>
                    </div>
                    
                    ${species.description ? `
                        <div class="mb-3">
                            <strong>Description:</strong><br>
                            <p>${species.description}</p>
                        </div>
                    ` : ''}
                    
                    <div class="d-flex gap-2">
                        <button class="btn btn-primary btn-sm" onclick="reportObservation(${species.id})">
                            <i class="fas fa-map-marker-alt me-1"></i>Report Observation
                        </button>
                        <button class="btn btn-outline-secondary btn-sm" onclick="downloadSpeciesData(${species.id})">
                            <i class="fas fa-download me-1"></i>Download Data
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    modal.show();
}

function reportObservation(speciesId) {
    // This would open a form to report a species observation
    alert(`Report observation feature for species ID ${speciesId} would be implemented here`);
}

function downloadSpeciesData(speciesId) {
    // This would trigger a download of species data
    alert(`Download species data feature for species ID ${speciesId} would be implemented here`);
}

function displaySpeciesError(message) {
    const container = document.getElementById('species-list');
    if (container) {
        container.innerHTML = `
            <div class="col-12 text-center py-4">
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle fa-2x mb-3"></i>
                    <h5>Error Loading Species Data</h5>
                    <p>${message}</p>
                    <button class="btn btn-outline-primary" onclick="loadSpeciesDatabase()">
                        <i class="fas fa-refresh me-1"></i>Retry
                    </button>
                </div>
            </div>
        `;
    }
}

// Utility functions
function getConfidenceColor(confidence) {
    if (confidence >= 90) return 'success';
    if (confidence >= 70) return 'info';
    if (confidence >= 50) return 'warning';
    return 'danger';
}

function getConservationStatusColor(status) {
    switch (status?.toLowerCase()) {
        case 'critically endangered':
        case 'critical':
            return 'danger';
        case 'endangered':
            return 'warning';
        case 'vulnerable':
            return 'info';
        case 'near threatened':
            return 'secondary';
        case 'least concern':
            return 'success';
        default:
            return 'dark';
    }
}

function getThreatLevelColor(level) {
    switch (level?.toLowerCase()) {
        case 'critical':
            return 'danger';
        case 'high':
            return 'warning';
        case 'medium':
            return 'info';
        case 'low':
            return 'success';
        default:
            return 'secondary';
    }
}

function getThreatLevelMapColor(level) {
    switch (level?.toLowerCase()) {
        case 'critical':
            return '#dc3545';
        case 'endangered':
        case 'high':
            return '#fd7e14';
        case 'vulnerable':
        case 'medium':
            return '#ffc107';
        case 'low':
            return '#198754';
        default:
            return '#6c757d';
    }
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showError(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger alert-dismissible fade show';
    alert.innerHTML = `
        <i class="fas fa-exclamation-triangle me-2"></i>${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alert, container.firstChild);
    }
}

// Export functions for global access
window.initializeSpeciesPage = initializeSpeciesPage;
window.viewSpeciesDetails = viewSpeciesDetails;
window.reportObservation = reportObservation;
window.downloadSpeciesData = downloadSpeciesData;
