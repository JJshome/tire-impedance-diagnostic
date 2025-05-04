#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tire Impedance Alert System Module
Based on Ucaretron Inc. patent application: "Tire Condition Diagnostic System and Method Using Impedance Measurement"

This module generates appropriate alerts based on detected tire anomalies:
- Immediate alerts for critical issues
- Advisory alerts for maintenance planning
- Diagnostics information for mechanics
"""

import time
from datetime import datetime
from enum import Enum, auto


class AlertLevel(Enum):
    """Enumeration of different alert severity levels."""
    INFO = auto()        # Informational alerts, no immediate action needed
    ADVISORY = auto()    # Advisory alerts suggesting future maintenance
    WARNING = auto()     # Warning alerts requiring attention soon
    CRITICAL = auto()    # Critical alerts requiring immediate attention
    EMERGENCY = auto()   # Emergency alerts requiring immediate stop


class TireAlertSystem:
    """
    Generates and manages alerts based on tire anomaly detection results.
    
    Attributes:
        alert_history (list): List of alerts generated
        alert_thresholds (dict): Confidence thresholds for different alert levels
    """
    
    def __init__(self):
        """Initialize the tire alert system."""
        self.alert_history = []
        
        # Confidence thresholds for different alert levels
        self.alert_thresholds = {
            AlertLevel.INFO: 0.2,
            AlertLevel.ADVISORY: 0.4,
            AlertLevel.WARNING: 0.6,
            AlertLevel.CRITICAL: 0.8,
            AlertLevel.EMERGENCY: 0.9
        }
        
        # Define mapping from anomaly types to alert levels
        self.anomaly_to_alert_level = {
            'NORMAL': AlertLevel.INFO,
            'GRADUAL_WEAR': AlertLevel.INFO,
            'ACCELERATED_WEAR': AlertLevel.ADVISORY,
            'SIDEWALL_DAMAGE': AlertLevel.CRITICAL,
            'TREAD_DAMAGE': AlertLevel.WARNING,
            'BEAD_DAMAGE': AlertLevel.CRITICAL,
            'PUNCTURE': AlertLevel.EMERGENCY,
            'UNEVEN_WEAR': AlertLevel.ADVISORY,
            'TEMPERATURE_ISSUE': AlertLevel.WARNING,
            'UNKNOWN': AlertLevel.WARNING
        }
    
    def generate_alerts(self, anomaly_results):
        """
        Generate alerts based on anomaly detection results.
        
        Args:
            anomaly_results (dict): Results from anomaly detection
            
        Returns:
            list: List of generated alerts
        """
        alerts = []
        
        timestamp = anomaly_results['timestamp']
        time_step = anomaly_results['time_step']
        
        # Process anomalies for each sensor
        for sensor_id, anomaly in anomaly_results['anomalies'].items():
            if anomaly['anomaly_detected']:
                # Determine alert level based on anomaly type and confidence
                anomaly_type = anomaly['anomaly_type'].name
                confidence = anomaly['confidence']
                
                # Get base alert level for this anomaly type
                base_level = self.anomaly_to_alert_level.get(anomaly_type, AlertLevel.WARNING)
                
                # Adjust level based on confidence
                adjusted_level = self._adjust_alert_level(base_level, confidence)
                
                # Create alert
                alert = {
                    'timestamp': timestamp,
                    'time_step': time_step,
                    'sensor_id': sensor_id,
                    'anomaly_type': anomaly_type,
                    'confidence': confidence,
                    'alert_level': adjusted_level,
                    'message': self._generate_alert_message(
                        sensor_id, anomaly_type, adjusted_level, 
                        confidence, anomaly['details']
                    ),
                    'recommendation': self._generate_recommendation(
                        sensor_id, anomaly_type, adjusted_level, confidence
                    )
                }
                
                alerts.append(alert)
                self.alert_history.append(alert)
        
        return alerts
    
    def _adjust_alert_level(self, base_level, confidence):
        """
        Adjust alert level based on confidence score.
        
        Args:
            base_level (AlertLevel): Base alert level for this anomaly type
            confidence (float): Confidence score for the anomaly
            
        Returns:
            AlertLevel: Adjusted alert level
        """
        # Get the ordinal value of the base level
        level_value = list(AlertLevel).index(base_level)
        
        # Increase level if confidence is very high
        if confidence > self.alert_thresholds[AlertLevel.EMERGENCY]:
            level_value = min(level_value + 1, len(AlertLevel) - 1)
        # Decrease level if confidence is low
        elif confidence < self.alert_thresholds[AlertLevel.ADVISORY]:
            level_value = max(level_value - 1, 0)
        
        # Return adjusted level
        return list(AlertLevel)[level_value]
    
    def _generate_alert_message(self, sensor_id, anomaly_type, alert_level, 
                               confidence, details):
        """
        Generate an appropriate alert message.
        
        Args:
            sensor_id (int): ID of the sensor reporting the anomaly
            anomaly_type (str): Type of anomaly detected
            alert_level (AlertLevel): Level of alert
            confidence (float): Confidence score for the anomaly
            details (str): Additional details about the anomaly
            
        Returns:
            str: Alert message
        """
        # Get location description
        location = self._get_location_description(sensor_id)
        
        # Format confidence as percentage
        confidence_pct = f"{confidence * 100:.0f}%"
        
        # Create appropriate prefix based on alert level
        if alert_level == AlertLevel.EMERGENCY:
            prefix = "EMERGENCY"
        elif alert_level == AlertLevel.CRITICAL:
            prefix = "CRITICAL ALERT"
        elif alert_level == AlertLevel.WARNING:
            prefix = "WARNING"
        elif alert_level == AlertLevel.ADVISORY:
            prefix = "ADVISORY"
        else:
            prefix = "INFO"
        
        # Construct message
        message = f"{prefix}: {anomaly_type} detected in {location} " \
                  f"(Confidence: {confidence_pct}). {details}"
        
        return message
    
    def _generate_recommendation(self, sensor_id, anomaly_type, alert_level, confidence):
        """
        Generate a recommendation based on the anomaly.
        
        Args:
            sensor_id (int): ID of the sensor reporting the anomaly
            anomaly_type (str): Type of anomaly detected
            alert_level (AlertLevel): Level of alert
            confidence (float): Confidence score for the anomaly
            
        Returns:
            str: Recommendation message
        """
        # Generate recommendations based on alert level and anomaly type
        if alert_level == AlertLevel.EMERGENCY:
            return "STOP VEHICLE IMMEDIATELY and inspect tire. Contact roadside assistance."
            
        elif alert_level == AlertLevel.CRITICAL:
            if anomaly_type == 'SIDEWALL_DAMAGE':
                return "Reduce speed immediately. Schedule urgent tire replacement."
            elif anomaly_type == 'BEAD_DAMAGE':
                return "Reduce speed and avoid sharp turns. Schedule urgent tire inspection."
            else:
                return "Reduce speed and schedule urgent tire inspection."
                
        elif alert_level == AlertLevel.WARNING:
            if anomaly_type == 'TREAD_DAMAGE':
                return "Schedule tire inspection within next 100 miles."
            elif anomaly_type == 'TEMPERATURE_ISSUE':
                return "Check tire pressure and reduce speed if temperature continues to rise."
            else:
                return "Schedule tire inspection at next opportunity."
                
        elif alert_level == AlertLevel.ADVISORY:
            if anomaly_type == 'ACCELERATED_WEAR':
                return "Schedule regular tire maintenance. Consider tire rotation."
            elif anomaly_type == 'UNEVEN_WEAR':
                return "Schedule tire rotation and alignment check."
            else:
                return "Monitor condition. Schedule regular maintenance."
                
        else:  # INFO level
            return "No immediate action needed. Continue regular tire maintenance."
    
    def _get_location_description(self, sensor_id):
        """
        Get a human-readable description of the sensor location.
        
        Args:
            sensor_id (int): ID of the sensor
            
        Returns:
            str: Human-readable location description
        """
        locations = {
            1: "left side of tire tread",
            2: "right side of tire tread",
            3: "tire sidewall",
            4: "tire bead area"
        }
        return locations.get(sensor_id, "unknown tire location")
    
    def alert_vehicle_system(self, alerts):
        """
        Simulate alerting the vehicle's central system.
        
        In a real implementation, this would communicate with the vehicle's
        dashboard display, central computer, or ADAS systems.
        
        Args:
            alerts (list): List of alerts to send to the vehicle system
            
        Returns:
            bool: True if alerts were successfully sent
        """
        # In a real system, this would integrate with the vehicle's communication bus
        # For simulation, we just print the alerts
        if alerts:
            print("\n=== ALERTS SENT TO VEHICLE SYSTEM ===")
            for alert in alerts:
                print(f"[{alert['alert_level'].name}] {alert['message']}")
            print("=====================================\n")
        
        return True
    
    def get_maintenance_report(self):
        """
        Generate a maintenance report based on alert history.
        
        Returns:
            str: Maintenance report text
        """
        # Count alerts by type and level
        alert_counts = {}
        for alert in self.alert_history:
            anomaly_type = alert['anomaly_type']
            if anomaly_type not in alert_counts:
                alert_counts[anomaly_type] = 0
            alert_counts[anomaly_type] += 1
        
        # Generate report
        report = "TIRE MAINTENANCE REPORT\n"
        report += f"Generated: {datetime.now()}\n"
        report += f"Total alerts: {len(self.alert_history)}\n\n"
        
        # Add alert statistics
        report += "Alert Statistics:\n"
        for anomaly_type, count in alert_counts.items():
            report += f"- {anomaly_type}: {count} alerts\n"
        
        # Add recommendations based on alert history
        report += "\nMaintenance Recommendations:\n"
        
        if any(a['alert_level'] in [AlertLevel.EMERGENCY, AlertLevel.CRITICAL] 
               for a in self.alert_history):
            report += "- URGENT: Immediate tire replacement recommended\n"
        elif any(a['alert_level'] == AlertLevel.WARNING for a in self.alert_history):
            report += "- Schedule tire inspection within 1 week\n"
        elif any(a['alert_level'] == AlertLevel.ADVISORY for a in self.alert_history):
            report += "- Schedule tire rotation and inspection at next service\n"
        else:
            report += "- Continue regular tire maintenance as scheduled\n"
        
        # Check for specific conditions
        if any(a['anomaly_type'] == 'UNEVEN_WEAR' for a in self.alert_history):
            report += "- Wheel alignment check recommended\n"
        
        if any(a['anomaly_type'] == 'TEMPERATURE_ISSUE' for a in self.alert_history):
            report += "- Tire pressure check recommended\n"
            
        return report


# Example usage if run directly
if __name__ == "__main__":
    # Import required modules for demonstration
    from sensor_simulation import TireImpedanceSensorArray
    from data_preprocessing import ImpedanceDataPreprocessor
    from anomaly_detection import TireAnomalyDetector
    
    # Initialize components
    sensor_array = TireImpedanceSensorArray()
    preprocessor = ImpedanceDataPreprocessor(window_size=5)
    detector = TireAnomalyDetector(history_length=10)
    alert_system = TireAlertSystem()
    
    # Simulate normal operation
    print("Simulating normal operation...")
    for i in range(5):
        # Collect and process data
        raw_data = sensor_array.collect_data()
        processed_data = preprocessor.preprocess_data(raw_data)
        
        # Analyze for anomalies
        anomaly_results = detector.analyze_data(processed_data)
        
        # Generate alerts
        alerts = alert_system.generate_alerts(anomaly_results)
        
        # Send alerts to vehicle system
        alert_system.alert_vehicle_system(alerts)
        
        time.sleep(0.5)  # Short delay for demonstration
    
    # Simulate sidewall damage
    print("\nSimulating sidewall damage...")
    sensor_array.simulate_damage(3, 'sidewall')
    
    # Collect more data after damage
    for i in range(5):
        # Collect and process data
        raw_data = sensor_array.collect_data()
        processed_data = preprocessor.preprocess_data(raw_data)
        
        # Analyze for anomalies
        anomaly_results = detector.analyze_data(processed_data)
        
        # Generate alerts
        alerts = alert_system.generate_alerts(anomaly_results)
        
        # Send alerts to vehicle system
        alert_system.alert_vehicle_system(alerts)
        
        time.sleep(0.5)  # Short delay for demonstration
    
    # Simulate tread damage
    print("\nSimulating tread damage...")
    sensor_array.simulate_damage(1, 'wear')
    
    # Collect more data after damage
    for i in range(5):
        # Collect and process data
        raw_data = sensor_array.collect_data()
        processed_data = preprocessor.preprocess_data(raw_data)
        
        # Analyze for anomalies
        anomaly_results = detector.analyze_data(processed_data)
        
        # Generate alerts
        alerts = alert_system.generate_alerts(anomaly_results)
        
        # Send alerts to vehicle system
        alert_system.alert_vehicle_system(alerts)
        
        time.sleep(0.5)  # Short delay for demonstration
    
    # Generate maintenance report
    print("\n" + alert_system.get_maintenance_report())
