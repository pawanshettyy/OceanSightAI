// Marine Biodiversity Platform - Dashboard JavaScript
// Handles oceanographic data visualization and dashboard interactions

let oceanDataCache = {};
let sustainabilityMetricsCache = {};
let dashboardCharts = {};

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
});

function initializeDashboard() {
    setupEventListeners();
    loadInitialData();
    updateMetricsDisplay();
    
    // Set up periodic data refresh
    setInterval(refreshDashboardData, 30000); // Refresh every 30 seconds
}

function setupEventListeners() {
    // Ocean data type buttons
    document.getElementById('btn-temperature')?.addEventListener('click', () => switchDataType('temperature'));
    document.getElementById('btn-currents')?.addEventListener('click', () => switchDataType('currents'));
    document.getElementById('btn-salinity')?.addEventListener('click', () => switchDataType('salinity'));
    document.getElementById('btn-ph')?.addEventListener('click', () => switchDataType('ph'));
}

function loadInitialData() {
    Promise.all([
        loadOceanData(),
        loadSustainabilityMetrics(),
        loadAlerts(),
        loadBiodiversityData()
    ]).then(() => {
        console.log('Dashboard data loaded successfully');
    }).catch(error => {
        console.error('Error loading dashboard data:', error);
        showErrorMessage('Failed to load dashboard data');
    });
}

function loadOceanData() {
    return fetch('/api/ocean-data')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            oceanDataCache = data;
            updateOceanMetrics(data);
            updateTemperatureChart(data.temperature_data);
            return data;
        })
        .catch(error => {
            console.error('Error loading ocean data:', error);
            displayDataError('ocean-metrics', 'Unable to load ocean data');
            throw error;
        });
}

function loadSustainabilityMetrics() {
    return fetch('/api/sustainability-metrics')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            sustainabilityMetricsCache = data;
            updateSustainabilityDisplay(data);
            updateHealthDistributionChart(data.ecosystem_health_distribution);
            return data;
        })
        .catch(error => {
            console.error('Error loading sustainability metrics:', error);
            displayDataError('sustainability-metrics', 'Unable to load sustainability metrics');
            throw error;
        });
}

function loadBiodiversityData() {
    return fetch('/api/biodiversity-index')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            updateBiodiversityChart(data);
            return data;
        })
        .catch(error => {
            console.error('Error loading biodiversity data:', error);
            displayDataError('biodiversity-chart', 'Unable to load biodiversity data');
            throw error;
        });
}

function loadAlerts() {
    return fetch('/api/alerts')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(alerts => {
            updateAlertsDisplay(alerts);
            return alerts;
        })
        .catch(error => {
            console.error('Error loading alerts:', error);
            displayDataError('alerts-container', 'Unable to load alerts');
            throw error;
        });
}

function updateOceanMetrics(data) {
    if (!data) return;
    
    try {
        // Calculate average temperature
        if (data.temperature_data && data.temperature_data.length > 0) {
            const avgTemp = data.temperature_data.reduce((sum, point) => sum + point.value, 0) / data.temperature_data.length;
            updateElement('avg-temp', `${avgTemp.toFixed(1)}°C`);
        } else {
            updateElement('avg-temp', 'No data');
        }
        
        // Calculate average salinity
        if (data.salinity_data && data.salinity_data.length > 0) {
            const avgSalinity = data.salinity_data.reduce((sum, point) => sum + point.value, 0) / data.salinity_data.length;
            updateElement('avg-salinity', `${avgSalinity.toFixed(1)}‰`);
        } else {
            updateElement('avg-salinity', 'No data');
        }
        
        // Calculate average pH
        if (data.ph_data && data.ph_data.length > 0) {
            const avgPH = data.ph_data.reduce((sum, point) => sum + point.value, 0) / data.ph_data.length;
            updateElement('avg-ph', avgPH.toFixed(2));
        } else {
            updateElement('avg-ph', 'No data');
        }
        
        // Calculate ocean health score
        const healthScore = calculateOceanHealthScore(data);
        updateElement('ocean-health', `${healthScore}%`);
        
    } catch (error) {
        console.error('Error updating ocean metrics:', error);
    }
}

function updateSustainabilityDisplay(data) {
    if (!data) return;
    
    try {
        updateElement('sustainability-score', `${data.sustainability_score}%`);
        updateElement('species-monitored', data.total_species);
        updateElement('threatened-species', data.threatened_species);
        updateElement('recent-observations', data.recent_observations);
        updateElement('active-alerts', data.total_active_alerts);
        
        // Update trend indicator
        const trendElement = document.getElementById('trend-indicator');
        if (trendElement && data.sustainability_trend) {
            const trend = data.sustainability_trend;
            let icon, color;
            
            switch (trend.status) {
                case 'improving':
                    icon = 'fas fa-arrow-up';
                    color = 'text-success';
                    break;
                case 'declining':
                    icon = 'fas fa-arrow-down';
                    color = 'text-danger';
                    break;
                default:
                    icon = 'fas fa-minus';
                    color = 'text-muted';
            }
            
            trendElement.innerHTML = `<i class="${icon} ${color}"></i>`;
            trendElement.title = `${trend.status} (${trend.percentage}%)`;
        }
        
    } catch (error) {
        console.error('Error updating sustainability display:', error);
    }
}

function updateAlertsDisplay(alerts) {
    const container = document.getElementById('alerts-container');
    const countElement = document.getElementById('alert-count');
    
    if (!container) return;
    
    try {
        if (!alerts || alerts.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted py-3">
                    <i class="fas fa-check-circle fa-2x mb-2"></i>
                    <p>No active alerts</p>
                </div>
            `;
            if (countElement) countElement.textContent = '0';
            return;
        }
        
        if (countElement) countElement.textContent = alerts.length;
        
        container.innerHTML = alerts.slice(0, 5).map(alert => `
            <div class="alert alert-${getSeverityClass(alert.severity)} alert-sm mb-2">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <strong>${alert.title}</strong>
                        <p class="mb-1 small">${alert.description}</p>
                        <small class="text-muted">
                            ${alert.location ? `<i class="fas fa-map-marker-alt me-1"></i>${alert.location} • ` : ''}
                            ${formatDate(alert.created_at)}
                        </small>
                    </div>
                    <span class="badge bg-${getSeverityClass(alert.severity)}">${alert.severity}</span>
                </div>
            </div>
        `).join('');
        
        if (alerts.length > 5) {
            container.innerHTML += `
                <div class="text-center mt-2">
                    <a href="/alerts" class="btn btn-outline-primary btn-sm">
                        View all ${alerts.length} alerts
                    </a>
                </div>
            `;
        }
        
    } catch (error) {
        console.error('Error updating alerts display:', error);
        container.innerHTML = '<div class="text-danger">Error loading alerts</div>';
    }
}

function updateTemperatureChart(temperatureData) {
    const ctx = document.getElementById('temperature-chart');
    if (!ctx) return;
    
    try {
        // Destroy existing chart if it exists
        if (dashboardCharts.temperatureChart) {
            dashboardCharts.temperatureChart.destroy();
        }
        
        if (!temperatureData || temperatureData.length === 0) {
            ctx.getContext('2d').fillText('No temperature data available', 10, 50);
            return;
        }
        
        // Group data by date and calculate averages
        const groupedData = temperatureData.reduce((acc, point) => {
            const date = new Date(point.timestamp).toDateString();
            if (!acc[date]) {
                acc[date] = { sum: 0, count: 0 };
            }
            acc[date].sum += point.value;
            acc[date].count += 1;
            return acc;
        }, {});
        
        const labels = Object.keys(groupedData).sort().slice(-7); // Last 7 days
        const data = labels.map(date => (groupedData[date].sum / groupedData[date].count).toFixed(1));
        
        dashboardCharts.temperatureChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels.map(date => new Date(date).toLocaleDateString()),
                datasets: [{
                    label: 'Average Temperature (°C)',
                    data: data,
                    borderColor: 'rgb(54, 162, 235)',
                    backgroundColor: 'rgba(54, 162, 235, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: 'Temperature (°C)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    }
                }
            }
        });
        
    } catch (error) {
        console.error('Error updating temperature chart:', error);
        displayChartError(ctx, 'Error loading temperature chart');
    }
}

function updateHealthDistributionChart(healthData) {
    const ctx = document.getElementById('health-distribution-chart');
    if (!ctx) return;
    
    try {
        // Destroy existing chart if it exists
        if (dashboardCharts.healthChart) {
            dashboardCharts.healthChart.destroy();
        }
        
        if (!healthData || Object.keys(healthData).length === 0) {
            displayChartError(ctx, 'No ecosystem health data available');
            return;
        }
        
        const labels = Object.keys(healthData);
        const data = Object.values(healthData);
        const colors = labels.map(label => getHealthColor(label));
        
        dashboardCharts.healthChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels.map(label => label.charAt(0).toUpperCase() + label.slice(1)),
                datasets: [{
                    data: data,
                    backgroundColor: colors,
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
        
    } catch (error) {
        console.error('Error updating health distribution chart:', error);
        displayChartError(ctx, 'Error loading health distribution chart');
    }
}

function updateBiodiversityChart(biodiversityData) {
    const ctx = document.getElementById('biodiversity-chart');
    if (!ctx) return;
    
    try {
        // Destroy existing chart if it exists
        if (dashboardCharts.biodiversityChart) {
            dashboardCharts.biodiversityChart.destroy();
        }
        
        if (!biodiversityData || biodiversityData.length === 0) {
            displayChartError(ctx, 'No biodiversity data available');
            return;
        }
        
        const labels = biodiversityData.map(item => item.region_name);
        const scores = biodiversityData.map(item => item.biodiversity_score);
        
        dashboardCharts.biodiversityChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Biodiversity Score',
                    data: scores,
                    backgroundColor: scores.map(score => getBiodiversityColor(score)),
                    borderColor: scores.map(score => getBiodiversityColor(score)),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Biodiversity Score'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Region'
                        }
                    }
                }
            }
        });
        
    } catch (error) {
        console.error('Error updating biodiversity chart:', error);
        displayChartError(ctx, 'Error loading biodiversity chart');
    }
}

function switchDataType(dataType) {
    // Update active button
    document.querySelectorAll('[id^="btn-"]').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`btn-${dataType}`).classList.add('active');
    
    // Update map display based on data type
    if (window.updateMapDataType) {
        window.updateMapDataType(dataType);
    }
}

function calculateOceanHealthScore(data) {
    try {
        let score = 100;
        let factors = 0;
        
        // Temperature factor (ideal range: 20-25°C)
        if (data.temperature_data && data.temperature_data.length > 0) {
            const avgTemp = data.temperature_data.reduce((sum, point) => sum + point.value, 0) / data.temperature_data.length;
            if (avgTemp < 15 || avgTemp > 30) score -= 20;
            else if (avgTemp < 18 || avgTemp > 27) score -= 10;
            factors++;
        }
        
        // pH factor (ideal range: 8.0-8.3)
        if (data.ph_data && data.ph_data.length > 0) {
            const avgPH = data.ph_data.reduce((sum, point) => sum + point.value, 0) / data.ph_data.length;
            if (avgPH < 7.5 || avgPH > 8.5) score -= 20;
            else if (avgPH < 7.8 || avgPH > 8.3) score -= 10;
            factors++;
        }
        
        // Salinity factor (normal range: 33-37‰)
        if (data.salinity_data && data.salinity_data.length > 0) {
            const avgSalinity = data.salinity_data.reduce((sum, point) => sum + point.value, 0) / data.salinity_data.length;
            if (avgSalinity < 30 || avgSalinity > 40) score -= 15;
            else if (avgSalinity < 32 || avgSalinity > 38) score -= 5;
            factors++;
        }
        
        return Math.max(0, Math.round(score));
        
    } catch (error) {
        console.error('Error calculating ocean health score:', error);
        return 0;
    }
}

function refreshDashboardData() {
    // Silently refresh data without showing loading indicators
    loadOceanData().catch(() => {});
    loadSustainabilityMetrics().catch(() => {});
    loadAlerts().catch(() => {});
}

function updateMetricsDisplay() {
    const now = new Date();
    const lastUpdate = document.getElementById('last-update');
    if (lastUpdate) {
        lastUpdate.textContent = `Last updated: ${now.toLocaleTimeString()}`;
    }
}

// Utility functions
function updateElement(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = value;
        element.classList.add('data-update');
        setTimeout(() => element.classList.remove('data-update'), 1000);
    }
}

function displayDataError(containerId, message) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = `
            <div class="text-center text-danger py-3">
                <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
                <p>${message}</p>
                <button class="btn btn-outline-primary btn-sm" onclick="location.reload()">
                    <i class="fas fa-refresh me-1"></i>Retry
                </button>
            </div>
        `;
    }
}

function displayChartError(canvas, message) {
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#dc3545';
    ctx.font = '14px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(message, canvas.width / 2, canvas.height / 2);
}

function getSeverityClass(severity) {
    switch (severity) {
        case 'critical': return 'danger';
        case 'high': return 'warning';
        case 'medium': return 'info';
        case 'low': return 'secondary';
        default: return 'secondary';
    }
}

function getHealthColor(health) {
    switch (health.toLowerCase()) {
        case 'excellent': return '#198754';
        case 'good': return '#20c997';
        case 'fair': return '#ffc107';
        case 'poor': return '#fd7e14';
        case 'critical': return '#dc3545';
        default: return '#6c757d';
    }
}

function getBiodiversityColor(score) {
    if (score >= 80) return '#198754';
    if (score >= 60) return '#20c997';
    if (score >= 40) return '#ffc107';
    if (score >= 20) return '#fd7e14';
    return '#dc3545';
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleString();
}

function showErrorMessage(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger alert-dismissible fade show';
    alert.innerHTML = `
        <i class="fas fa-exclamation-triangle me-2"></i>${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container-fluid');
    if (container) {
        container.insertBefore(alert, container.firstChild);
    }
}
