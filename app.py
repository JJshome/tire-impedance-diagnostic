#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tire Condition Diagnostic System - Web Interface
Based on Ucaretron Inc. patent application: "Tire Condition Diagnostic System and Method Using Impedance Measurement"

This module provides a web-based interface to the tire diagnostic system using Flask.
It allows users to:
- Run simulations with different damage scenarios
- View real-time visualizations
- Access historical data and reports
"""

import os
import time
import json
import threading
import tempfile
from datetime import datetime
import base64
from io import BytesIO

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt

# Import the simulation components
from sensor_simulation import TireImpedanceSensorArray
from data_preprocessing import ImpedanceDataPreprocessor
from anomaly_detection import TireAnomalyDetector, AnomalyType
from alert_system import TireAlertSystem, AlertLevel
from data_visualization import TireDataVisualizer

# Create Flask app
app = Flask(__name__)

# Global variables for simulation state
simulation_running = False
simulation_thread = None
simulation_data = {
    'time_steps': [],
    'sensor_readings': {
        1: [],  # Tread Left
        2: [],  # Tread Right
        3: [],  # Sidewall
        4: []   # Bead
    },
    'alerts': [],
    'current_status': 'Ready',
    'damage_applied': False
}

# Ensure output directories exist
os.makedirs('output', exist_ok=True)
os.makedirs('static/images', exist_ok=True)

# Initialize components
sensor_array = TireImpedanceSensorArray()
preprocessor = ImpedanceDataPreprocessor(window_size=10)
detector = TireAnomalyDetector(history_length=20)
alert_system = TireAlertSystem()
visualizer = TireDataVisualizer(history_size=50)

def reset_simulation_data():
    """Reset simulation data to initial state."""
    global simulation_data
    simulation_data = {
        'time_steps': [],
        'sensor_readings': {
            1: [],  # Tread Left
            2: [],  # Tread Right
            3: [],  # Sidewall
            4: []   # Bead
        },
        'alerts': [],
        'current_status': 'Ready',
        'damage_applied': False
    }
    
    # Reset simulation components
    global sensor_array, preprocessor, detector, alert_system, visualizer
    sensor_array = TireImpedanceSensorArray()
    preprocessor = ImpedanceDataPreprocessor(window_size=10)
    detector = TireAnomalyDetector(history_length=20)
    alert_system = TireAlertSystem()
    visualizer = TireDataVisualizer(history_size=50)

def simulate_damage(damage_type):
    """Simulate damage based on the specified type."""
    global simulation_data
    
    if damage_type == 'sidewall':
        sensor_array.simulate_damage(3, 'sidewall')
        message = "Simulated sidewall damage"
    elif damage_type == 'tread':
        sensor_array.simulate_damage(1, 'tread')
        message = "Simulated tread damage on left side"
    elif damage_type == 'puncture':
        sensor_array.simulate_damage(1, 'puncture')
        sensor_array.simulate_damage(2, 'puncture')
        message = "Simulated puncture damage"
    elif damage_type == 'wear':
        sensor_array.simulate_damage(1, 'wear')
        sensor_array.simulate_damage(2, 'wear')
        message = "Simulated accelerated wear"
    else:
        message = f"Unknown damage type: {damage_type}"
    
    simulation_data['damage_applied'] = True
    simulation_data['current_status'] = message
    return message

def simulation_worker(interval, steps, damage_time, damage_type):
    """Background worker function for running simulations."""
    global simulation_running, simulation_data
    
    simulation_data['current_status'] = 'Simulation started'
    damage_step = damage_time // interval
    
    try:
        for step in range(steps):
            if not simulation_running:
                break
            
            # Collect and process data
            raw_data = sensor_array.collect_data()
            processed_data = preprocessor.preprocess_data(raw_data)
            anomaly_results = detector.analyze_data(processed_data)
            alerts = alert_system.generate_alerts(anomaly_results)
            
            # Update visualization data
            visualizer.update_data(processed_data, anomaly_results)
            
            # Update simulation data
            simulation_data['time_steps'].append(processed_data['time_step'])
            
            for sensor_id, reading in processed_data['readings'].items():
                simulation_data['sensor_readings'][sensor_id].append({
                    'normalized_value': reading['normalized_value'],
                    'temperature': reading['temperature'],
                    'location': reading['location']
                })
            
            # Process alerts
            for alert in alerts:
                simulation_data['alerts'].append({
                    'time_step': processed_data['time_step'],
                    'sensor_id': alert['sensor_id'],
                    'level': alert['alert_level'].name,
                    'message': alert['message'],
                    'recommendation': alert['recommendation']
                })
            
            # Apply damage if it's time
            if step == damage_step and not simulation_data['damage_applied']:
                message = simulate_damage(damage_type)
                simulation_data['current_status'] = message
            
            # Generate visualizations periodically
            if step % 5 == 0 or step == steps - 1:
                # Generate tire status visualization
                plt.figure(figsize=(8, 8))
                # Draw tire status using matplotlib
                fig = visualizer.visualize_tire_status(processed_data, anomaly_results)
                plt.close(fig)
                
                # Generate impedance plot
                fig = visualizer.plot_impedance_time_series()
                plt.close(fig)
            
            # Update status
            simulation_data['current_status'] = f"Running simulation - Step {step+1}/{steps}"
            
            # Sleep for the interval
            time.sleep(interval)
        
        # Simulation completed
        if simulation_running:
            simulation_data['current_status'] = "Simulation completed"
            
            # Generate final report
            report = alert_system.get_maintenance_report()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = os.path.join('output', f"maintenance_report_{timestamp}.txt")
            
            with open(report_path, 'w') as f:
                f.write(report)
    
    except Exception as e:
        simulation_data['current_status'] = f"Error in simulation: {str(e)}"
    
    finally:
        simulation_running = False

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/start_simulation', methods=['POST'])
def start_simulation():
    """Start a new simulation with specified parameters."""
    global simulation_running, simulation_thread
    
    if simulation_running:
        return jsonify({'status': 'error', 'message': 'Simulation already running'})
    
    # Get parameters from form
    interval = int(request.form.get('interval', 1))
    duration = int(request.form.get('duration', 30))
    damage_time = int(request.form.get('damage_time', 15))
    damage_type = request.form.get('damage_type', 'sidewall')
    
    # Reset simulation data
    reset_simulation_data()
    
    # Start simulation in background thread
    simulation_running = True
    steps = duration // interval
    simulation_thread = threading.Thread(
        target=simulation_worker,
        args=(interval, steps, damage_time, damage_type)
    )
    simulation_thread.daemon = True
    simulation_thread.start()
    
    return jsonify({
        'status': 'success',
        'message': f'Simulation started with {steps} steps, damage at step {damage_time//interval}'
    })

@app.route('/stop_simulation', methods=['POST'])
def stop_simulation():
    """Stop the currently running simulation."""
    global simulation_running
    
    if not simulation_running:
        return jsonify({'status': 'error', 'message': 'No simulation running'})
    
    simulation_running = False
    simulation_data['current_status'] = "Simulation stopped by user"
    
    return jsonify({'status': 'success', 'message': 'Simulation stopped'})

@app.route('/apply_damage', methods=['POST'])
def apply_damage():
    """Apply damage to the tire during simulation."""
    if not simulation_running:
        return jsonify({'status': 'error', 'message': 'No simulation running'})
    
    damage_type = request.form.get('damage_type', 'sidewall')
    message = simulate_damage(damage_type)
    
    return jsonify({'status': 'success', 'message': message})

@app.route('/simulation_status')
def simulation_status():
    """Get the current status of the simulation."""
    return jsonify({
        'running': simulation_running,
        'status': simulation_data['current_status'],
        'time_step': simulation_data['time_steps'][-1] if simulation_data['time_steps'] else 0,
        'total_steps': len(simulation_data['time_steps']),
        'damage_applied': simulation_data['damage_applied'],
        'alert_count': len(simulation_data['alerts'])
    })

@app.route('/sensor_data')
def sensor_data():
    """Get the latest sensor readings for display."""
    latest_readings = {}
    
    for sensor_id, readings in simulation_data['sensor_readings'].items():
        if readings:
            latest_readings[sensor_id] = readings[-1]
    
    return jsonify(latest_readings)

@app.route('/alerts')
def alerts():
    """Get all alerts from the simulation."""
    return jsonify(simulation_data['alerts'])

@app.route('/tire_status_image')
def tire_status_image():
    """Generate and return a tire status visualization."""
    if not simulation_data['time_steps']:
        # Return default image if no data
        fig, ax = plt.subplots(figsize=(8, 8))
        circle = plt.Circle((0.5, 0.5), 0.4, fill=False, color='gray')
        ax.add_patch(circle)
        ax.text(0.5, 0.5, "No Data", ha='center', va='center', fontsize=14)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Save to BytesIO
        buf = BytesIO()
        fig.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        
        return send_file(buf, mimetype='image/png')
    
    # Generate tire status visualization using the latest data
    if visualizer.history[1]:  # Check if we have history data
        fig = visualizer.visualize_tire_status(None, None)
        
        # Save to BytesIO
        buf = BytesIO()
        fig.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        
        return send_file(buf, mimetype='image/png')
    else:
        # Return empty image if no visualization data
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.text(0.5, 0.5, "Waiting for data...", ha='center', va='center', fontsize=14)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # Save to BytesIO
        buf = BytesIO()
        fig.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        
        return send_file(buf, mimetype='image/png')

@app.route('/impedance_plot')
def impedance_plot():
    """Generate and return an impedance time series plot."""
    if not simulation_data['time_steps']:
        # Return default image if no data
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "No Data", ha='center', va='center', fontsize=14)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # Save to BytesIO
        buf = BytesIO()
        fig.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        
        return send_file(buf, mimetype='image/png')
    
    # Generate impedance plot using the latest data
    fig = visualizer.plot_impedance_time_series()
    
    # Save to BytesIO
    buf = BytesIO()
    fig.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    
    return send_file(buf, mimetype='image/png')

@app.route('/download_report')
def download_report():
    """Generate and download the latest maintenance report."""
    if not simulation_data['time_steps']:
        return jsonify({'status': 'error', 'message': 'No simulation data available'})
    
    # Generate report
    report = alert_system.get_maintenance_report()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join('output', f"maintenance_report_{timestamp}.txt")
    
    with open(report_path, 'w') as f:
        f.write(report)
    
    return send_file(report_path, as_attachment=True)

@app.route('/download_csv')
def download_csv():
    """Download the simulation data as a CSV file."""
    if not simulation_data['time_steps']:
        return jsonify({'status': 'error', 'message': 'No simulation data available'})
    
    # Create a CSV file with the simulation data
    import csv
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join('output', f"simulation_data_{timestamp}.csv")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Write header
        writer.writerow(['time_step', 'sensor_id', 'location', 'normalized_value', 'temperature'])
        
        # Write data
        for i, time_step in enumerate(simulation_data['time_steps']):
            for sensor_id, readings in simulation_data['sensor_readings'].items():
                if i < len(readings):
                    writer.writerow([
                        time_step,
                        sensor_id,
                        readings[i]['location'],
                        readings[i]['normalized_value'],
                        readings[i]['temperature']
                    ])
    
    return send_file(csv_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
