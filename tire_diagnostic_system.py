#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tire Condition Diagnostic System Using Impedance Measurement
Based on Ucaretron Inc. patent application: "Tire Condition Diagnostic System and Method Using Impedance Measurement"

This is the main application file that integrates all modules:
- Sensor data collection
- Data preprocessing
- Anomaly detection
- Alert generation
- Data visualization

The system simulates 4 impedance sensors in a tire, collecting data every 30 seconds
to detect anomalies and generate appropriate alerts.
"""

import time
import os
import argparse
from datetime import datetime

# Import modules
from sensor_simulation import TireImpedanceSensorArray
from data_preprocessing import ImpedanceDataPreprocessor
from anomaly_detection import TireAnomalyDetector
from alert_system import TireAlertSystem
from data_visualization import TireDataVisualizer


class TireDiagnosticSystem:
    """
    Integrated tire diagnostic system that combines all components.
    
    Attributes:
        sensor_array (TireImpedanceSensorArray): Sensor data collection
        preprocessor (ImpedanceDataPreprocessor): Data preprocessing
        detector (TireAnomalyDetector): Anomaly detection
        alert_system (TireAlertSystem): Alert generation
        visualizer (TireDataVisualizer): Data visualization
        data_collection_interval (int): Interval between data collections in seconds
        output_dir (str): Directory for output files
    """
    
    def __init__(self, data_collection_interval=30, output_dir='output'):
        """
        Initialize the tire diagnostic system.
        
        Args:
            data_collection_interval (int): Time between readings in seconds
            output_dir (str): Directory to store output files
        """
        print("Initializing Tire Condition Diagnostic System...")
        
        # Initialize components
        self.sensor_array = TireImpedanceSensorArray()
        self.preprocessor = ImpedanceDataPreprocessor(window_size=10)
        self.detector = TireAnomalyDetector(history_length=20)
        self.alert_system = TireAlertSystem()
        self.visualizer = TireDataVisualizer(history_size=50)
        
        # Configuration
        self.data_collection_interval = data_collection_interval
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        print(f"System initialized with data collection interval of {data_collection_interval} seconds")
        print(f"Output files will be saved to: {os.path.abspath(output_dir)}")
    
    def collect_and_process_data(self):
        """
        Collect and process a single data point from all sensors.
        
        Returns:
            tuple: (raw_data, processed_data, anomaly_results, alerts)
        """
        # 1. Collect raw sensor data
        raw_data = self.sensor_array.collect_data()
        
        # 2. Preprocess the data
        processed_data = self.preprocessor.preprocess_data(raw_data)
        
        # 3. Detect anomalies
        anomaly_results = self.detector.analyze_data(processed_data)
        
        # 4. Generate alerts if anomalies were detected
        alerts = self.alert_system.generate_alerts(anomaly_results)
        
        # 5. Update visualization data
        self.visualizer.update_data(processed_data, anomaly_results)
        
        return raw_data, processed_data, anomaly_results, alerts
    
    def display_readings(self, processed_data):
        """
        Display current sensor readings in the console.
        
        Args:
            processed_data (dict): Dictionary with preprocessed sensor readings
        """
        print(f"\n=== Time Step {processed_data['time_step']} - "
              f"{processed_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} ===")
        
        for sensor_id, reading in processed_data['readings'].items():
            print(f"Sensor {sensor_id} ({reading['location']}):")
            print(f"  Normalized impedance: {reading['normalized_value']:.3f}")
            print(f"  Temperature: {reading['temperature']:.1f}°C")
    
    def handle_alerts(self, alerts):
        """
        Process and display alerts.
        
        Args:
            alerts (list): List of alerts from the alert system
        """
        if alerts:
            # Log alerts to console
            print("\n!!! ALERTS DETECTED !!!")
            for alert in alerts:
                print(f"[{alert['alert_level'].name}] {alert['message']}")
                print(f"Recommendation: {alert['recommendation']}")
                
            # Send alerts to vehicle system (simulated)
            self.alert_system.alert_vehicle_system(alerts)
            
            # Save visualization with alerts
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.visualizer.plot_all_visualizations(None, None, 
                                                  directory=self.output_dir)
    
    def generate_maintenance_report(self):
        """
        Generate and save a maintenance report.
        
        Returns:
            str: Path to the saved report file
        """
        report = self.alert_system.get_maintenance_report()
        
        # Save report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(self.output_dir, f"maintenance_report_{timestamp}.txt")
        
        with open(report_path, 'w') as f:
            f.write(report)
        
        print(f"\nMaintenance report saved to: {report_path}")
        return report_path
    
    def simulate_damage(self, scenario='sidewall'):
        """
        Simulate tire damage for testing.
        
        Args:
            scenario (str): Type of damage to simulate
                ('sidewall', 'tread', 'puncture', 'wear')
        """
        print(f"\n*** Simulating {scenario} damage ***")
        
        if scenario == 'sidewall':
            # Simulate sidewall damage
            self.sensor_array.simulate_damage(3, 'sidewall')
        elif scenario == 'tread':
            # Simulate tread damage on left side
            self.sensor_array.simulate_damage(1, 'tread')
        elif scenario == 'puncture':
            # Simulate puncture
            self.sensor_array.simulate_damage(1, 'puncture')
            self.sensor_array.simulate_damage(2, 'puncture')
        elif scenario == 'wear':
            # Simulate accelerated wear
            self.sensor_array.simulate_damage(1, 'wear')
            self.sensor_array.simulate_damage(2, 'wear')
        else:
            print(f"Unknown damage scenario: {scenario}")
    
    def run_simulation(self, duration=300, damage_time=150, damage_type='sidewall', 
                      visualize=True):
        """
        Run the diagnostic system simulation for a specified duration.
        
        Args:
            duration (int): Total duration of simulation in seconds
            damage_time (int): When to simulate damage, in seconds from start
            damage_type (str): Type of damage to simulate
            visualize (bool): Whether to display visualization at the end
            
        Returns:
            str: Path to the maintenance report file
        """
        print(f"Starting tire diagnostic system simulation...")
        print(f"Simulation will run for {duration} seconds")
        print(f"Damage will be simulated after {damage_time} seconds")
        
        # Calculate number of iterations based on collection interval
        iterations = duration // self.data_collection_interval
        damage_iteration = damage_time // self.data_collection_interval
        
        start_time = time.time()
        
        try:
            for i in range(iterations):
                # Collect and process data
                raw_data, processed_data, anomaly_results, alerts = (
                    self.collect_and_process_data())
                
                # Display current readings
                self.display_readings(processed_data)
                
                # Handle any alerts
                self.handle_alerts(alerts)
                
                # Simulate damage at the specified time
                if i == damage_iteration:
                    self.simulate_damage(damage_type)
                
                # Store visualization periodically
                if i % 10 == 0:
                    self.visualizer.plot_all_visualizations(
                        processed_data, anomaly_results, directory=self.output_dir)
                
                # Wait for next collection cycle (adjusted for processing time)
                elapsed = time.time() - start_time
                next_collection = (i + 1) * self.data_collection_interval
                sleep_time = max(0, next_collection - elapsed)
                
                if sleep_time > 0:
                    print(f"Waiting {sleep_time:.1f} seconds until next reading...")
                    time.sleep(sleep_time)
            
            # Generate final maintenance report
            report_path = self.generate_maintenance_report()
            
            # Generate and show final visualizations
            if visualize:
                print("Generating final visualizations...")
                figs = self.visualizer.plot_all_visualizations(
                    processed_data, anomaly_results, directory=self.output_dir)
                self.visualizer.display_plots()
            
            print("Simulation completed successfully")
            return report_path
            
        except KeyboardInterrupt:
            print("\nSimulation interrupted by user")
            self.generate_maintenance_report()
            return None


def main():
    """Main function to run the tire diagnostic system."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Tire Condition Diagnostic System Simulation')
    
    parser.add_argument('--interval', type=int, default=5,
                        help='Data collection interval in seconds (default: 5)')
    parser.add_argument('--duration', type=int, default=60,
                        help='Simulation duration in seconds (default: 60)')
    parser.add_argument('--damage-time', type=int, default=30,
                        help='When to simulate damage, in seconds from start (default: 30)')
    parser.add_argument('--damage-type', type=str, default='sidewall',
                        choices=['sidewall', 'tread', 'puncture', 'wear'],
                        help='Type of damage to simulate (default: sidewall)')
    parser.add_argument('--output-dir', type=str, default='output',
                        help='Directory for output files (default: output)')
    parser.add_argument('--no-visualize', action='store_true',
                        help='Do not display visualizations at the end')
    
    args = parser.parse_args()
    
    # Create and run the diagnostic system
    system = TireDiagnosticSystem(
        data_collection_interval=args.interval,
        output_dir=args.output_dir
    )
    
    system.run_simulation(
        duration=args.duration,
        damage_time=args.damage_time,
        damage_type=args.damage_type,
        visualize=not args.no_visualize
    )


if __name__ == "__main__":
    # Print patent information header
    print("=" * 80)
    print("Tire Condition Diagnostic System Using Impedance Measurement")
    print("Based on Ucaretron Inc. patent application")
    print("=" * 80)
    print("\nUSAGE EXAMPLES:")
    print("  python tire_diagnostic_system.py")
    print("  python tire_diagnostic_system.py --interval 10 --duration 120 --damage-time 60")
    print("  python tire_diagnostic_system.py --damage-type tread --no-visualize")
    print("-" * 80)
    
    # Run the main function
    main()
