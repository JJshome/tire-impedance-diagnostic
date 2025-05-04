#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tire Impedance Data Visualization Module
Based on Ucaretron Inc. patent application: "Tire Condition Diagnostic System and Method Using Impedance Measurement"

This module provides visualization tools for tire impedance data:
- Time series plots of impedance readings
- Anomaly visualization
- Tire status representation
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from matplotlib.patches import Circle, Wedge, Rectangle
import time
from datetime import datetime, timedelta


class TireDataVisualizer:
    """
    Visualizes tire impedance data and anomaly detection results.
    
    Attributes:
        history_size (int): Number of data points to keep in visualization history
        impedance_history (dict): Dictionary storing historical impedance data
        anomaly_history (dict): Dictionary storing historical anomaly data
        temperature_history (dict): Dictionary storing historical temperature data
    """
    
    def __init__(self, history_size=30):
        """
        Initialize the data visualizer.
        
        Args:
            history_size (int): Maximum number of data points to keep in history
        """
        self.history_size = history_size
        
        # Initialize data storage
        self.impedance_history = {
            1: {'values': [], 'timestamps': []},  # Sensor 1 (tread_left)
            2: {'values': [], 'timestamps': []},  # Sensor 2 (tread_right)
            3: {'values': [], 'timestamps': []},  # Sensor 3 (sidewall)
            4: {'values': [], 'timestamps': []}   # Sensor 4 (bead)
        }
        
        self.anomaly_history = {
            1: {'values': [], 'timestamps': [], 'types': []},
            2: {'values': [], 'timestamps': [], 'types': []},
            3: {'values': [], 'timestamps': [], 'types': []},
            4: {'values': [], 'timestamps': [], 'types': []}
        }
        
        self.temperature_history = {
            1: {'values': [], 'timestamps': []},
            2: {'values': [], 'timestamps': []},
            3: {'values': [], 'timestamps': []},
            4: {'values': [], 'timestamps': []}
        }
        
        # Sensor location descriptions
        self.sensor_locations = {
            1: 'Tread (Left)',
            2: 'Tread (Right)',
            3: 'Sidewall',
            4: 'Bead'
        }
        
        # Color mapping for different sensors
        self.sensor_colors = {
            1: 'blue',
            2: 'green',
            3: 'red',
            4: 'purple'
        }
    
    def update_data(self, processed_data, anomaly_results):
        """
        Update the visualization data with new readings.
        
        Args:
            processed_data (dict): Dictionary with preprocessed sensor readings
            anomaly_results (dict): Dictionary with anomaly detection results
        """
        timestamp = processed_data['timestamp']
        
        # Update impedance and temperature history
        for sensor_id, reading in processed_data['readings'].items():
            # Get normalized impedance value
            impedance = reading['normalized_value']
            
            # Update impedance history
            self.impedance_history[sensor_id]['values'].append(impedance)
            self.impedance_history[sensor_id]['timestamps'].append(timestamp)
            
            # Limit history size
            if len(self.impedance_history[sensor_id]['values']) > self.history_size:
                self.impedance_history[sensor_id]['values'].pop(0)
                self.impedance_history[sensor_id]['timestamps'].pop(0)
            
            # Update temperature history
            temp = reading['temperature']
            self.temperature_history[sensor_id]['values'].append(temp)
            self.temperature_history[sensor_id]['timestamps'].append(timestamp)
            
            # Limit history size
            if len(self.temperature_history[sensor_id]['values']) > self.history_size:
                self.temperature_history[sensor_id]['values'].pop(0)
                self.temperature_history[sensor_id]['timestamps'].pop(0)
        
        # Update anomaly history
        for sensor_id, anomaly in anomaly_results['anomalies'].items():
            if anomaly['anomaly_detected']:
                # Record anomaly
                self.anomaly_history[sensor_id]['values'].append(
                    processed_data['readings'][sensor_id]['normalized_value']
                )
                self.anomaly_history[sensor_id]['timestamps'].append(timestamp)
                self.anomaly_history[sensor_id]['types'].append(anomaly['anomaly_type'])
                
                # Limit history size
                if len(self.anomaly_history[sensor_id]['values']) > self.history_size:
                    self.anomaly_history[sensor_id]['values'].pop(0)
                    self.anomaly_history[sensor_id]['timestamps'].pop(0)
                    self.anomaly_history[sensor_id]['types'].pop(0)
    
    def plot_impedance_time_series(self, save_path=None):
        """
        Plot time series of impedance readings for all sensors.
        
        Args:
            save_path (str, optional): Path to save plot image
            
        Returns:
            matplotlib.figure.Figure: Figure object for the plot
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot impedance data for each sensor
        for sensor_id in self.impedance_history:
            values = self.impedance_history[sensor_id]['values']
            timestamps = self.impedance_history[sensor_id]['timestamps']
            
            if values:  # Only plot if we have data
                label = self.sensor_locations[sensor_id]
                color = self.sensor_colors[sensor_id]
                ax.plot(timestamps, values, 'o-', label=label, color=color)
                
                # Plot anomalies with different marker
                anomaly_values = self.anomaly_history[sensor_id]['values']
                anomaly_timestamps = self.anomaly_history[sensor_id]['timestamps']
                anomaly_types = self.anomaly_history[sensor_id]['types']
                
                if anomaly_values:
                    ax.scatter(anomaly_timestamps, anomaly_values, marker='*', 
                              s=120, color=color, edgecolor='black', linewidth=1.5,
                              label=f"{label} Anomalies" if anomaly_values else "")
        
        # Add labels and title
        ax.set_title('Tire Impedance Readings Over Time', fontsize=14)
        ax.set_xlabel('Time', fontsize=12)
        ax.set_ylabel('Normalized Impedance', fontsize=12)
        
        # Format the x-axis to show readable timestamps
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        
        # Add grid and legend
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend(loc='upper left')
        
        # Add threshold line
        ax.axhline(y=1.3, color='red', linestyle='--', alpha=0.6, 
                  label='Alert Threshold')
        
        plt.tight_layout()
        
        # Save plot if path is provided
        if save_path:
            plt.savefig(save_path)
        
        return fig
    
    def plot_temperature_time_series(self, save_path=None):
        """
        Plot time series of temperature readings for all sensors.
        
        Args:
            save_path (str, optional): Path to save plot image
            
        Returns:
            matplotlib.figure.Figure: Figure object for the plot
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot temperature data for each sensor
        for sensor_id in self.temperature_history:
            values = self.temperature_history[sensor_id]['values']
            timestamps = self.temperature_history[sensor_id]['timestamps']
            
            if values:  # Only plot if we have data
                label = self.sensor_locations[sensor_id]
                color = self.sensor_colors[sensor_id]
                ax.plot(timestamps, values, 'o-', label=label, color=color)
        
        # Add labels and title
        ax.set_title('Tire Temperature Readings Over Time', fontsize=14)
        ax.set_xlabel('Time', fontsize=12)
        ax.set_ylabel('Temperature (°C)', fontsize=12)
        
        # Format the x-axis to show readable timestamps
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        
        # Add grid and legend
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend(loc='upper left')
        
        # Add threshold lines
        ax.axhline(y=65, color='red', linestyle='--', alpha=0.6, 
                  label='High Temperature Threshold')
        ax.axhline(y=5, color='blue', linestyle='--', alpha=0.6, 
                  label='Low Temperature Threshold')
        
        plt.tight_layout()
        
        # Save plot if path is provided
        if save_path:
            plt.savefig(save_path)
        
        return fig
    
    def visualize_tire_status(self, processed_data, anomaly_results, save_path=None):
        """
        Create a visual representation of the tire with sensor readings and anomalies.
        
        Args:
            processed_data (dict): Dictionary with preprocessed sensor readings
            anomaly_results (dict): Dictionary with anomaly detection results
            save_path (str, optional): Path to save plot image
            
        Returns:
            matplotlib.figure.Figure: Figure object for the plot
        """
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # Set plot bounds
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-1.2, 1.2)
        
        # Draw tire outline
        tire_outline = Circle((0, 0), 1, fill=False, linewidth=2, color='black')
        ax.add_patch(tire_outline)
        
        # Draw rim
        rim = Circle((0, 0), 0.4, fill=True, color='lightgray', alpha=0.6)
        ax.add_patch(rim)
        
        # Draw tread area
        tread = Circle((0, 0), 1, fill=True, color='gray', alpha=0.2)
        ax.add_patch(tread)
        
        # Draw sensor positions and status
        sensor_positions = {
            1: (-0.5, 0.5),    # Tread left
            2: (0.5, 0.5),     # Tread right
            3: (0, 0.9),       # Sidewall
            4: (0, 0.4)        # Bead
        }
        
        for sensor_id, position in sensor_positions.items():
            # Get sensor data
            reading = processed_data['readings'][sensor_id]
            normalized_value = reading['normalized_value']
            
            # Check if anomaly was detected
            anomaly = anomaly_results['anomalies'][sensor_id]
            has_anomaly = anomaly['anomaly_detected']
            
            # Set color based on normalized value and anomaly status
            if has_anomaly:
                color = 'red'
                size = 0.1
            else:
                # Color gradient from green to yellow to red
                if normalized_value < 1.1:
                    color = 'green'
                elif normalized_value < 1.2:
                    color = 'yellow'
                else:
                    color = 'orange'
                size = 0.08
            
            # Draw sensor
            sensor = Circle(position, size, fill=True, color=color, alpha=0.8)
            ax.add_patch(sensor)
            
            # Add sensor label
            plt.text(position[0], position[1], str(sensor_id), 
                    ha='center', va='center', fontsize=10, color='white')
            
            # Add reading value near the sensor
            plt.text(position[0], position[1] - 0.15, f"{normalized_value:.2f}", 
                    ha='center', va='center', fontsize=8)
        
        # Add title and legend
        ax.set_title('Tire Status Visualization', fontsize=14)
        ax.axis('equal')
        ax.axis('off')
        
        # Add a legend
        legend_elements = [
            Circle((0, 0), 0.05, color='green', alpha=0.8),
            Circle((0, 0), 0.05, color='yellow', alpha=0.8),
            Circle((0, 0), 0.05, color='orange', alpha=0.8),
            Circle((0, 0), 0.05, color='red', alpha=0.8)
        ]
        
        legend_labels = [
            'Normal',
            'Caution',
            'Warning',
            'Anomaly Detected'
        ]
        
        ax.legend(legend_elements, legend_labels, loc='lower center', 
                 bbox_to_anchor=(0.5, -0.1), ncol=4)
        
        # Save plot if path is provided
        if save_path:
            plt.savefig(save_path)
        
        return fig
    
    def plot_all_visualizations(self, processed_data, anomaly_results, directory=None):
        """
        Create all visualization plots.
        
        Args:
            processed_data (dict): Dictionary with preprocessed sensor readings
            anomaly_results (dict): Dictionary with anomaly detection results
            directory (str, optional): Directory to save plot images
            
        Returns:
            dict: Dictionary with figure objects
        """
        # Create plots
        imp_fig = self.plot_impedance_time_series(
            save_path=f"{directory}/impedance_plot.png" if directory else None
        )
        
        temp_fig = self.plot_temperature_time_series(
            save_path=f"{directory}/temperature_plot.png" if directory else None
        )
        
        status_fig = self.visualize_tire_status(
            processed_data, anomaly_results,
            save_path=f"{directory}/tire_status.png" if directory else None
        )
        
        return {
            'impedance': imp_fig,
            'temperature': temp_fig,
            'status': status_fig
        }
    
    def display_plots(self):
        """Display all plots."""
        plt.show()


# Example usage if run directly
if __name__ == "__main__":
    # Import required modules for demonstration
    from sensor_simulation import TireImpedanceSensorArray
    from data_preprocessing import ImpedanceDataPreprocessor
    from anomaly_detection import TireAnomalyDetector
    
    # Initialize components
    sensor_array = TireImpedanceSensorArray()
    preprocessor = ImpedanceDataPreprocessor(window_size=5)
    detector = TireAnomalyDetector(history_length=20)
    visualizer = TireDataVisualizer(history_size=20)
    
    # Simulate normal operation for a while
    print("Simulating normal operation...")
    for i in range(15):
        # Collect and process data
        raw_data = sensor_array.collect_data()
        processed_data = preprocessor.preprocess_data(raw_data)
        anomaly_results = detector.analyze_data(processed_data)
        
        # Update visualization data
        visualizer.update_data(processed_data, anomaly_results)
        
        time.sleep(0.1)  # Short delay for simulation
    
    # Create plots for normal operation
    print("Creating visualizations for normal operation...")
    visualizer.plot_all_visualizations(processed_data, anomaly_results)
    
    # Simulate damage
    print("\nSimulating sidewall damage...")
    sensor_array.simulate_damage(3, 'sidewall')
    
    # Collect more data after damage
    for i in range(10):
        # Collect and process data
        raw_data = sensor_array.collect_data()
        processed_data = preprocessor.preprocess_data(raw_data)
        anomaly_results = detector.analyze_data(processed_data)
        
        # Update visualization data
        visualizer.update_data(processed_data, anomaly_results)
        
        time.sleep(0.1)  # Short delay for simulation
    
    # Create final plots after damage
    print("Creating visualizations after damage...")
    visualizer.plot_all_visualizations(processed_data, anomaly_results)
    
    # Display plots
    visualizer.display_plots()
