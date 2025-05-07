/**
 * Tire Condition Diagnostic System - Simulation Controller
 * Based on Ucaretron Inc. patent application
 * 
 * This JavaScript file manages the simulation interface:
 * - Controls simulation start/stop
 * - Updates visualization in real-time
 * - Handles user interactions
 * - Displays alerts and sensor readings
 */

// Global simulation state
let simulationState = {
    running: false,
    statusPollInterval: null,
    dataPollInterval: null,
    visualizationUpdateInterval: null,
    timeStep: 0,
    damageApplied: false,
    alertCount: 0
};

// Initialize the application when document is ready
$(document).ready(function() {
    // Attach event handlers
    setupEventHandlers();
    
    // Initial UI setup
    updateUIState();
    
    // Load initial visualizations
    updateVisualizations();
    
    console.log("Tire Diagnostic System Initialized");
});

/**
 * Set up all event handlers for user interactions
 */
function setupEventHandlers() {
    // Start simulation button
    $('#start-btn').click(function() {
        if (simulationState.running) return;
        startSimulation();
    });
    
    // Stop simulation button
    $('#stop-btn').click(function() {
        if (!simulationState.running) return;
        stopSimulation();
    });
    
    // Apply damage button
    $('#damage-btn').click(function() {
        if (!simulationState.running) return;
        applyDamage();
    });
    
    // Download report button
    $('#download-report-btn').click(function() {
        window.location.href = '/download_report';
    });
    
    // Download CSV button
    $('#download-csv-btn').click(function() {
        window.location.href = '/download_csv';
    });
    
    // Form validation
    $('#simulation-form').submit(function(e) {
        e.preventDefault();
        if (!simulationState.running) {
            startSimulation();
        }
    });
    
    // Responsive image handling
    $('.tire-status-img, .impedance-plot-img').on('click', function() {
        // Could implement lightbox or modal for larger view
        console.log("Image clicked - could show enlarged view");
    });
}

/**
 * Start the simulation with parameters from the form
 */
function startSimulation() {
    // Show loader
    $('#status-loader').show();
    
    // Get form data
    let formData = $('#simulation-form').serialize();
    
    // Send start request
    $.ajax({
        url: '/start_simulation',
        type: 'POST',
        data: formData,
        success: function(response) {
            if (response.status === 'success') {
                simulationState.running = true;
                $('#simulation-status').text(response.message);
                
                // Update UI
                updateUIState();
                
                // Start polling for updates
                startPolling();
            } else {
                $('#simulation-status').text('Error: ' + response.message);
                $('#status-loader').hide();
            }
        },
        error: function(xhr, status, error) {
            $('#simulation-status').text('Server error: ' + error);
            $('#status-loader').hide();
        }
    });
}

/**
 * Stop the currently running simulation
 */
function stopSimulation() {
    if (!simulationState.running) return;
    
    $.ajax({
        url: '/stop_simulation',
        type: 'POST',
        success: function(response) {
            if (response.status === 'success') {
                simulationState.running = false;
                $('#simulation-status').text(response.message);
                
                // Update UI
                updateUIState();
                
                // Stop polling
                stopPolling();
            } else {
                $('#simulation-status').text('Error: ' + response.message);
            }
        },
        error: function(xhr, status, error) {
            $('#simulation-status').text('Server error: ' + error);
        }
    });
}

/**
 * Apply damage to the tire during simulation
 */
function applyDamage() {
    if (!simulationState.running) return;
    
    let damageType = $('#damage-type').val();
    
    $.ajax({
        url: '/apply_damage',
        type: 'POST',
        data: { damage_type: damageType },
        success: function(response) {
            if (response.status === 'success') {
                $('#simulation-status').text(response.message);
                simulationState.damageApplied = true;
                $('#damage-btn').prop('disabled', true);
            } else {
                $('#simulation-status').text('Error: ' + response.message);
            }
        },
        error: function(xhr, status, error) {
            $('#simulation-status').text('Server error: ' + error);
        }
    });
}

/**
 * Start polling for simulation updates
 */
function startPolling() {
    // Poll for status updates every second
    simulationState.statusPollInterval = setInterval(updateStatus, 1000);
    
    // Poll for data updates every second
    simulationState.dataPollInterval = setInterval(updateData, 1000);
    
    // Update visualizations every 2 seconds
    simulationState.visualizationUpdateInterval = setInterval(updateVisualizations, 2000);
}

/**
 * Stop all polling intervals
 */
function stopPolling() {
    clearInterval(simulationState.statusPollInterval);
    clearInterval(simulationState.dataPollInterval);
    clearInterval(simulationState.visualizationUpdateInterval);
    $('#status-loader').hide();
}

/**
 * Update the simulation status from the server
 */
function updateStatus() {
    $.ajax({
        url: '/simulation_status',
        type: 'GET',
        success: function(data) {
            $('#simulation-status').text(data.status);
            $('#time-step').text(data.time_step);
            $('#alert-count').text(data.alert_count);
            
            simulationState.timeStep = data.time_step;
            simulationState.alertCount = data.alert_count;
            
            // Check if simulation stopped on the server
            if (!data.running && simulationState.running) {
                simulationState.running = false;
                updateUIState();
                stopPolling();
            }
            
            // Update damage button if damage already applied
            if (data.damage_applied) {
                simulationState.damageApplied = true;
                $('#damage-btn').prop('disabled', true);
            }
        },
        error: function(xhr, status, error) {
            console.error("Error fetching status:", error);
            $('#simulation-status').text('Error fetching status');
        }
    });
}

/**
 * Update sensor data and alerts from the server
 */
function updateData() {
    // Update sensor readings
    $.ajax({
        url: '/sensor_data',
        type: 'GET',
        success: function(data) {
            for (let sensorId in data) {
                let reading = data[sensorId];
                let normalizedValue = reading.normalized_value.toFixed(3);
                let temperature = reading.temperature.toFixed(1);
                
                $(`#sensor-${sensorId}-value`).text(normalizedValue);
                $(`#sensor-${sensorId}-temp`).text(temperature);
                
                // Update card color based on value
                let cardElement = $(`#sensor-${sensorId}-card`);
                cardElement.removeClass('normal warning critical');
                
                if (normalizedValue > 1.3) {
                    cardElement.addClass('critical');
                } else if (normalizedValue > 1.1) {
                    cardElement.addClass('warning');
                } else {
                    cardElement.addClass('normal');
                }
            }
        },
        error: function(xhr, status, error) {
            console.error("Error fetching sensor data:", error);
        }
    });
    
    // Update alerts
    $.ajax({
        url: '/alerts',
        type: 'GET',
        success: function(data) {
            if (data.length > 0) {
                let alertsHtml = '';
                
                // Display most recent alerts first
                for (let i = data.length - 1; i >= 0; i--) {
                    let alert = data[i];
                    alertsHtml += generateAlertHTML(alert);
                }
                
                $('#alerts-container').html(alertsHtml);
            }
        },
        error: function(xhr, status, error) {
            console.error("Error fetching alerts:", error);
        }
    });
}

/**
 * Generate HTML for an alert
 */
function generateAlertHTML(alert) {
    return `
        <div class="alert-item ${alert.level}">
            <strong>${alert.level}:</strong> ${alert.message}<br>
            <small>Recommendation: ${alert.recommendation}</small>
        </div>
    `;
}

/**
 * Update the visualization images
 */
function updateVisualizations() {
    // Add timestamp to prevent caching
    let timestamp = new Date().getTime();
    $('#tire-status-img').attr('src', '/tire_status_image?' + timestamp);
    $('#impedance-plot-img').attr('src', '/impedance_plot?' + timestamp);
}

/**
 * Update UI state based on simulation status
 */
function updateUIState() {
    if (simulationState.running) {
        // Simulation is running
        $('#start-btn').prop('disabled', true);
        $('#stop-btn').prop('disabled', false);
        $('#damage-btn').prop('disabled', simulationState.damageApplied);
        $('#download-report-btn').prop('disabled', true);
        $('#download-csv-btn').prop('disabled', true);
        
        // Disable form inputs
        $('#simulation-form input, #simulation-form select').prop('disabled', true);
    } else {
        // Simulation is stopped
        $('#start-btn').prop('disabled', false);
        $('#stop-btn').prop('disabled', true);
        $('#damage-btn').prop('disabled', true);
        $('#download-report-btn').prop('disabled', simulationState.timeStep === 0);
        $('#download-csv-btn').prop('disabled', simulationState.timeStep === 0);
        
        // Enable form inputs
        $('#simulation-form input, #simulation-form select').prop('disabled', false);
    }
}

/**
 * Format a number with specified precision
 */
function formatNumber(value, precision = 3) {
    return Number(value).toFixed(precision);
}
