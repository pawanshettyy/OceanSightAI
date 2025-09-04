// Marine Biodiversity Platform - Charts JavaScript
// Chart utilities and configurations for data visualization

// Chart color schemes
const CHART_COLORS = {
    primary: '#0d6efd',
    secondary: '#6c757d',
    success: '#198754',
    danger: '#dc3545',
    warning: '#ffc107',
    info: '#0dcaf0',
    ocean: ['#0077be', '#003f5c', '#40e0d0', '#2d5a27', '#ff6b35'],
    temperature: ['#000080', '#0000ff', '#00ffff', '#00ff00', '#ffff00', '#ff8000', '#ff0000'],
    biodiversity: ['#dc3545', '#fd7e14', '#ffc107', '#20c997', '#198754']
};

// Chart default configurations
const CHART_DEFAULTS = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'bottom'
        },
        tooltip: {
            mode: 'index',
            intersect: false
        }
    },
    scales: {
        x: {
            grid: {
                color: 'rgba(255, 255, 255, 0.1)'
            }
        },
        y: {
            grid: {
                color: 'rgba(255, 255, 255, 0.1)'
            }
        }
    }
};

// Chart registry to keep track of created charts
const chartRegistry = {};

/**
 * Create a line chart for time series data
 */
function createTimeSeriesChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas element ${canvasId} not found`);
        return null;
    }
    
    // Destroy existing chart if it exists
    if (chartRegistry[canvasId]) {
        chartRegistry[canvasId].destroy();
    }
    
    const config = {
        type: 'line',
        data: data,
        options: {
            ...CHART_DEFAULTS,
            ...options,
            plugins: {
                ...CHART_DEFAULTS.plugins,
                ...options.plugins
            }
        }
    };
    
    const chart = new Chart(ctx, config);
    chartRegistry[canvasId] = chart;
    
    return chart;
}

/**
 * Create a bar chart
 */
function createBarChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas element ${canvasId} not found`);
        return null;
    }
    
    // Destroy existing chart if it exists
    if (chartRegistry[canvasId]) {
        chartRegistry[canvasId].destroy();
    }
    
    const config = {
        type: 'bar',
        data: data,
        options: {
            ...CHART_DEFAULTS,
            ...options,
            plugins: {
                ...CHART_DEFAULTS.plugins,
                ...options.plugins
            }
        }
    };
    
    const chart = new Chart(ctx, config);
    chartRegistry[canvasId] = chart;
    
    return chart;
}

/**
 * Create a doughnut chart
 */
function createDoughnutChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas element ${canvasId} not found`);
        return null;
    }
    
    // Destroy existing chart if it exists
    if (chartRegistry[canvasId]) {
        chartRegistry[canvasId].destroy();
    }
    
    const config = {
        type: 'doughnut',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            },
            ...options
        }
    };
    
    const chart = new Chart(ctx, config);
    chartRegistry[canvasId] = chart;
    
    return chart;
}

/**
 * Create a polar area chart
 */
function createPolarChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas element ${canvasId} not found`);
        return null;
    }
    
    // Destroy existing chart if it exists
    if (chartRegistry[canvasId]) {
        chartRegistry[canvasId].destroy();
    }
    
    const config = {
        type: 'polarArea',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            },
            ...options
        }
    };
    
    const chart = new Chart(ctx, config);
    chartRegistry[canvasId] = chart;
    
    return chart;
}

/**
 * Update existing chart data
 */
function updateChartData(canvasId, newData) {
    const chart = chartRegistry[canvasId];
    if (!chart) {
        console.error(`Chart ${canvasId} not found in registry`);
        return;
    }
    
    chart.data = newData;
    chart.update('active');
}

/**
 * Get color for biodiversity score
 */
function getBiodiversityScoreColor(score) {
    if (score >= 80) return CHART_COLORS.biodiversity[4]; // Green
    if (score >= 60) return CHART_COLORS.biodiversity[3]; // Teal
    if (score >= 40) return CHART_COLORS.biodiversity[2]; // Yellow
    if (score >= 20) return CHART_COLORS.biodiversity[1]; // Orange
    return CHART_COLORS.biodiversity[0]; // Red
}

/**
 * Get color for conservation status
 */
function getConservationStatusColor(status) {
    switch (status?.toLowerCase()) {
        case 'critically endangered':
        case 'critical':
            return CHART_COLORS.danger;
        case 'endangered':
            return CHART_COLORS.warning;
        case 'vulnerable':
            return CHART_COLORS.info;
        case 'near threatened':
            return CHART_COLORS.secondary;
        case 'least concern':
        case 'stable':
            return CHART_COLORS.success;
        default:
            return CHART_COLORS.secondary;
    }
}

/**
 * Get color for threat level
 */
function getThreatLevelColor(level) {
    switch (level?.toLowerCase()) {
        case 'critical':
            return CHART_COLORS.danger;
        case 'high':
            return CHART_COLORS.warning;
        case 'medium':
            return CHART_COLORS.info;
        case 'low':
            return CHART_COLORS.success;
        default:
            return CHART_COLORS.secondary;
    }
}

/**
 * Get temperature color based on value
 */
function getTemperatureChartColor(temperature) {
    const colors = CHART_COLORS.temperature;
    const tempRanges = [0, 5, 10, 15, 20, 25, 30];
    
    for (let i = 0; i < tempRanges.length - 1; i++) {
        if (temperature >= tempRanges[i] && temperature < tempRanges[i + 1]) {
            return colors[i];
        }
    }
    
    return colors[colors.length - 1];
}

/**
 * Create a sustainability metrics chart
 */
function createSustainabilityChart(canvasId, metricsData) {
    if (!metricsData) {
        displayChartError(canvasId, 'No sustainability data available');
        return;
    }
    
    const data = {
        labels: ['Overall Score', 'Species Health', 'Ocean Health', 'Fishing Sustainability'],
        datasets: [{
            label: 'Sustainability Metrics',
            data: [
                metricsData.sustainability_score || 0,
                metricsData.avg_biodiversity_score || 0,
                calculateOceanHealthFromMetrics(metricsData),
                calculateFishingSustainability(metricsData)
            ],
            backgroundColor: [
                getBiodiversityScoreColor(metricsData.sustainability_score || 0),
                getBiodiversityScoreColor(metricsData.avg_biodiversity_score || 0),
                CHART_COLORS.ocean[2],
                CHART_COLORS.ocean[3]
            ],
            borderColor: '#fff',
            borderWidth: 2
        }]
    };
    
    return createDoughnutChart(canvasId, data, {
        plugins: {
            legend: {
                position: 'bottom'
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        return `${context.label}: ${context.parsed}%`;
                    }
                }
            }
        }
    });
}

/**
 * Create species trend chart
 */
function createSpeciesTrendChart(canvasId, speciesData) {
    if (!speciesData || speciesData.length === 0) {
        displayChartError(canvasId, 'No species trend data available');
        return;
    }
    
    // Group species by conservation status
    const statusCounts = {};
    speciesData.forEach(species => {
        const status = species.conservation_status || 'Unknown';
        statusCounts[status] = (statusCounts[status] || 0) + 1;
    });
    
    const data = {
        labels: Object.keys(statusCounts),
        datasets: [{
            label: 'Species Count',
            data: Object.values(statusCounts),
            backgroundColor: Object.keys(statusCounts).map(status => getConservationStatusColor(status)),
            borderColor: '#fff',
            borderWidth: 2
        }]
    };
    
    return createDoughnutChart(canvasId, data);
}

/**
 * Create ocean parameter trends chart
 */
function createOceanParameterChart(canvasId, parameterData, parameterType) {
    if (!parameterData || parameterData.length === 0) {
        displayChartError(canvasId, `No ${parameterType} data available`);
        return;
    }
    
    // Sort data by timestamp
    const sortedData = parameterData.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    
    // Group by date and calculate daily averages
    const dailyData = {};
    sortedData.forEach(point => {
        const date = new Date(point.timestamp).toDateString();
        if (!dailyData[date]) {
            dailyData[date] = { sum: 0, count: 0 };
        }
        dailyData[date].sum += point.value;
        dailyData[date].count += 1;
    });
    
    const labels = Object.keys(dailyData).sort().slice(-30); // Last 30 days
    const values = labels.map(date => (dailyData[date].sum / dailyData[date].count).toFixed(2));
    
    const data = {
        labels: labels.map(date => new Date(date).toLocaleDateString()),
        datasets: [{
            label: `${parameterType} (Daily Average)`,
            data: values,
            borderColor: CHART_COLORS.primary,
            backgroundColor: `${CHART_COLORS.primary}20`,
            tension: 0.4,
            fill: true
        }]
    };
    
    return createTimeSeriesChart(canvasId, data, {
        scales: {
            y: {
                beginAtZero: false,
                title: {
                    display: true,
                    text: getParameterUnit(parameterType)
                }
            },
            x: {
                title: {
                    display: true,
                    text: 'Date'
                }
            }
        }
    });
}

/**
 * Create fishing pressure heatmap chart
 */
function createFishingPressureChart(canvasId, pressureData) {
    if (!pressureData || pressureData.length === 0) {
        displayChartError(canvasId, 'No fishing pressure data available');
        return;
    }
    
    const labels = pressureData.map(area => area.fishing_area);
    const pressureScores = pressureData.map(area => area.pressure_score);
    
    const data = {
        labels: labels,
        datasets: [{
            label: 'Fishing Pressure Score',
            data: pressureScores,
            backgroundColor: pressureScores.map(score => {
                if (score >= 80) return CHART_COLORS.danger;
                if (score >= 60) return CHART_COLORS.warning;
                if (score >= 40) return CHART_COLORS.info;
                return CHART_COLORS.success;
            }),
            borderColor: '#fff',
            borderWidth: 1
        }]
    };
    
    return createBarChart(canvasId, data, {
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
                    text: 'Pressure Score'
                }
            }
        }
    });
}

/**
 * Display error message on chart canvas
 */
function displayChartError(canvasId, message) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const canvasWidth = canvas.width;
    const canvasHeight = canvas.height;
    
    // Clear canvas
    ctx.clearRect(0, 0, canvasWidth, canvasHeight);
    
    // Set text style
    ctx.fillStyle = '#dc3545';
    ctx.font = '16px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    
    // Draw error message
    ctx.fillText(message, canvasWidth / 2, canvasHeight / 2);
    
    // Draw error icon
    ctx.font = '24px Arial';
    ctx.fillText('⚠', canvasWidth / 2, (canvasHeight / 2) - 30);
}

/**
 * Destroy all charts
 */
function destroyAllCharts() {
    Object.keys(chartRegistry).forEach(canvasId => {
        if (chartRegistry[canvasId]) {
            chartRegistry[canvasId].destroy();
            delete chartRegistry[canvasId];
        }
    });
}

/**
 * Helper functions
 */
function calculateOceanHealthFromMetrics(metrics) {
    // Simple calculation based on available metrics
    return Math.max(0, 100 - (metrics.total_active_alerts || 0) * 5);
}

function calculateFishingSustainability(metrics) {
    // Calculate based on threat percentage
    const threatPercentage = metrics.threat_percentage || 0;
    return Math.max(0, 100 - threatPercentage * 2);
}

function getParameterUnit(parameterType) {
    switch (parameterType.toLowerCase()) {
        case 'temperature': return 'Temperature (°C)';
        case 'salinity': return 'Salinity (‰)';
        case 'ph': return 'pH Level';
        case 'oxygen': return 'Oxygen (mg/L)';
        case 'depth': return 'Depth (m)';
        default: return 'Value';
    }
}

// Export functions for global access
window.createTimeSeriesChart = createTimeSeriesChart;
window.createBarChart = createBarChart;
window.createDoughnutChart = createDoughnutChart;
window.createPolarChart = createPolarChart;
window.updateChartData = updateChartData;
window.createSustainabilityChart = createSustainabilityChart;
window.createSpeciesTrendChart = createSpeciesTrendChart;
window.createOceanParameterChart = createOceanParameterChart;
window.createFishingPressureChart = createFishingPressureChart;
window.displayChartError = displayChartError;
window.destroyAllCharts = destroyAllCharts;
window.CHART_COLORS = CHART_COLORS;
