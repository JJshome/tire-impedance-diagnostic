#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tire Impedance Anomaly Detection Module
Based on Ucaretron Inc. patent application: "Tire Condition Diagnostic System and Method Using Impedance Measurement"

This module implements anomaly detection algorithms to identify tire issues:
- Threshold-based detection for immediate issues
- Rate-of-change detection for wear monitoring
- Pattern recognition for trend analysis
"""

import numpy as np
from collections import deque
import time
from enum import Enum


class AnomalyType(Enum):
    """Enumeration of different types of tire anomalies that can be detected."""
    NORMAL = 0
    GRADUAL_WEAR = 1      # Normal wear process
    ACCELERATED_WEAR = 2  # Faster than normal wear
    SIDEWALL_DAMAGE = 3   # Damage to the sidewall structure
    TREAD_DAMAGE = 4      # Damage to the tread
    BEAD_DAMAGE = 5       # Damage near the bead
    PUNCTURE = 6          # Possible puncture
    UNEVEN_WEAR = 7       # Uneven wear pattern
    TEMPERATURE_ISSUE = 8 # Abnormal temperature
    UNKNOWN = 9           # Unclassified anomaly


class TireAnomalyDetector:
    """
    Detects anomalies in tire impedance data.
    
    Attributes:
        history_length (int): Length of historical data to maintain
        history (dict): Dictionary of sensor readings history
        rate_history (dict): Dictionary of rate-of-change history
        thresholds (dict): Anomaly detection thresholds for each sensor
    """
    
    def __init__(self, history_length=30):
        """
        Initialize the anomaly detector.
        
        Args:
            history_length (int): Number of readings to keep in history
        """
        self.history_length = history_length
        
        # Initialize history storage for each sensor
        self.history = {
            1: deque(maxlen=history_length),  # Sensor 1 (tread_left)
            2: deque(maxlen=history_length),  # Sensor 2 (tread_right)
            3: deque(maxlen=history_length),  # Sensor 3 (sidewall)
            4: deque(maxlen=history_length)   # Sensor 4 (bead)
        }
        
        # Initialize rate-of-change history
        self.rate_history = {
            1: deque(maxlen=history_length),
            2: deque(maxlen=history_length),
            3: deque(maxlen=history_length),
            4: deque(maxlen=history_length)
        }
        
        # Set anomaly detection thresholds
        # These would be calibrated based on empirical data in a real system
        self.thresholds = {
            # Threshold values are for normalized readings (ratio to baseline)
            'tread_left': {
                'absolute_high': 1.3,    # Threshold for immediate alert
                'rate_high': 0.02,       # High rate of change
                'wear_rate_normal': 0.005 # Normal wear rate
            },
            'tread_right': {
                'absolute_high': 1.3,
                'rate_high': 0.02,
                'wear_rate_normal': 0.005
            },
            'sidewall': {
                'absolute_high': 1.4,    # Sidewall damage threshold
                'rate_high': 0.03,       # Rapid change indicates potential damage
                'wear_rate_normal': 0.003
            },
            'bead': {
                'absolute_high': 1.2,    # Bead area is more sensitive
                'rate_high': 0.01,
                'wear_rate_normal': 0.002
            },
            # Temperature thresholds (in Celsius)
            'temperature_high': 65.0,
            'temperature_low': 5.0
        }
    
    def update_history(self, processed_data):
        """
        Update the history with new processed data.
        
        Args:
            processed_data (dict): Dictionary with preprocessed sensor readings
        """
        for sensor_id, reading in processed_data['readings'].items():
            # Add normalized value to history
            self.history[sensor_id].append(reading['normalized_value'])
            
            # Calculate and store rate of change if we have at least 2 readings
            if len(self.history[sensor_id]) >= 2:
                current = self.history[sensor_id][-1]
                previous = self.history[sensor_id][-2]
                rate = current - previous
                self.rate_history[sensor_id].append(rate)
            else:
                # No previous reading, so rate is 0
                self.rate_history[sensor_id].append(0)
    
    def detect_threshold_anomalies(self, processed_data):
        """
        Detect anomalies based on absolute thresholds.
        
        Args:
            processed_data (dict): Dictionary with preprocessed sensor readings
            
        Returns:
            dict: Dictionary with anomaly detection results for each sensor
        """
        results = {}
        
        for sensor_id, reading in processed_data['readings'].items():
            location = reading['location']
            normalized_value = reading['normalized_value']
            temperature = reading['temperature']
            
            # Initialize result for this sensor
            results[sensor_id] = {
                'anomaly_detected': False,
                'anomaly_type': AnomalyType.NORMAL,
                'confidence': 0.0,
                'details': ""
            }
            
            # Check temperature thresholds
            if temperature > self.thresholds['temperature_high']:
                results[sensor_id] = {
                    'anomaly_detected': True,
                    'anomaly_type': AnomalyType.TEMPERATURE_ISSUE,
                    'confidence': min(1.0, (temperature - self.thresholds['temperature_high']) / 10.0),
                    'details': f"High temperature detected: {temperature:.1f}°C"
                }
                continue
            
            if temperature < self.thresholds['temperature_low']:
                results[sensor_id] = {
                    'anomaly_detected': True,
                    'anomaly_type': AnomalyType.TEMPERATURE_ISSUE,
                    'confidence': min(1.0, (self.thresholds['temperature_low'] - temperature) / 10.0),
                    'details': f"Low temperature detected: {temperature:.1f}°C"
                }
                continue
            
            # Check impedance absolute thresholds
            threshold = self.thresholds.get(location, {}).get('absolute_high', 1.3)
            
            if normalized_value > threshold:
                # Determine type of anomaly based on sensor location
                if location == 'sidewall':
                    anomaly_type = AnomalyType.SIDEWALL_DAMAGE
                    details = "Potential sidewall damage detected"
                elif location.startswith('tread'):
                    anomaly_type = AnomalyType.TREAD_DAMAGE
                    details = "Potential tread damage detected"
                elif location == 'bead':
                    anomaly_type = AnomalyType.BEAD_DAMAGE
                    details = "Potential bead area issue detected"
                else:
                    anomaly_type = AnomalyType.UNKNOWN
                    details = "Unknown anomaly detected"
                
                # Calculate confidence based on how far above threshold
                confidence = min(1.0, (normalized_value - threshold) / threshold)
                
                results[sensor_id] = {
                    'anomaly_detected': True,
                    'anomaly_type': anomaly_type,
                    'confidence': confidence,
                    'details': details
                }
        
        return results
    
    def detect_rate_anomalies(self, processed_data):
        """
        Detect anomalies based on rate of change.
        
        Args:
            processed_data (dict): Dictionary with preprocessed sensor readings
            
        Returns:
            dict: Dictionary with rate-based anomaly detection results
        """
        results = {}
        
        for sensor_id, reading in processed_data['readings'].items():
            location = reading['location']
            
            # Initialize result for this sensor
            results[sensor_id] = {
                'anomaly_detected': False,
                'anomaly_type': AnomalyType.NORMAL,
                'confidence': 0.0,
                'details': ""
            }
            
            # Skip if we don't have enough history
            if len(self.rate_history[sensor_id]) < 2:
                continue
            
            # Get current rate of change
            current_rate = self.rate_history[sensor_id][-1]
            
            # Get threshold for this location
            rate_threshold = self.thresholds.get(location, {}).get('rate_high', 0.02)
            
            if current_rate > rate_threshold:
                # Determine type of anomaly based on sensor location
                if location == 'sidewall':
                    anomaly_type = AnomalyType.SIDEWALL_DAMAGE
                    details = "Rapid sidewall impedance change detected"
                elif location.startswith('tread'):
                    anomaly_type = AnomalyType.ACCELERATED_WEAR
                    details = "Accelerated tread wear detected"
                elif location == 'bead':
                    anomaly_type = AnomalyType.BEAD_DAMAGE
                    details = "Rapid bead area impedance change detected"
                else:
                    anomaly_type = AnomalyType.UNKNOWN
                    details = "Rapid impedance change detected"
                
                # Calculate confidence based on rate
                confidence = min(1.0, current_rate / (rate_threshold * 2))
                
                results[sensor_id] = {
                    'anomaly_detected': True,
                    'anomaly_type': anomaly_type,
                    'confidence': confidence,
                    'details': details
                }
        
        return results
    
    def detect_trend_anomalies(self):
        """
        Detect anomalies based on long-term trends in the data.
        
        Returns:
            dict: Dictionary with trend-based anomaly detection results
        """
        results = {}
        
        # Analyze data for each sensor
        for sensor_id in self.history:
            # Initialize result for this sensor
            results[sensor_id] = {
                'anomaly_detected': False,
                'anomaly_type': AnomalyType.NORMAL,
                'confidence': 0.0,
                'details': ""
            }
            
            # Skip if we don't have enough history
            if len(self.history[sensor_id]) < self.history_length // 2:
                continue
            
            # Simple trend analysis: linear regression
            data = list(self.history[sensor_id])
            x = np.arange(len(data))
            
            # Check if all elements are the same
            if all(d == data[0] for d in data):
                continue
                
            # Calculate linear regression slope (simplified approach)
            # In a real system, a more robust regression would be used
            n = len(data)
            x_mean = np.mean(x)
            y_mean = np.mean(data)
            numerator = np.sum((x - x_mean) * (data - y_mean))
            denominator = np.sum((x - x_mean) ** 2)
            
            # Avoid division by zero
            if denominator == 0:
                continue
                
            slope = numerator / denominator
            
            # Get normal wear rate threshold for this sensor
            location = self._get_sensor_location(sensor_id)
            normal_wear_rate = self.thresholds.get(location, {}).get('wear_rate_normal', 0.005)
            
            # Detect abnormally high wear rate
            if slope > normal_wear_rate * 3:  # 3x normal wear rate
                results[sensor_id] = {
                    'anomaly_detected': True,
                    'anomaly_type': AnomalyType.ACCELERATED_WEAR,
                    'confidence': min(1.0, slope / (normal_wear_rate * 5)),
                    'details': "Long-term accelerated wear detected"
                }
        
        # Check for uneven wear across tread sensors
        if 1 in self.history and 2 in self.history and \
           len(self.history[1]) > 5 and len(self.history[2]) > 5:
            # Compare tread left and right
            left_avg = np.mean(list(self.history[1])[-5:])
            right_avg = np.mean(list(self.history[2])[-5:])
            
            # If significant difference, report uneven wear
            diff_ratio = abs(left_avg - right_avg) / max(left_avg, right_avg)
            if diff_ratio > 0.15:  # More than 15% difference
                # Determine which side is wearing faster
                higher_side = 1 if left_avg > right_avg else 2
                
                results[higher_side] = {
                    'anomaly_detected': True,
                    'anomaly_type': AnomalyType.UNEVEN_WEAR,
                    'confidence': min(1.0, diff_ratio / 0.3),
                    'details': f"Uneven tread wear detected ({diff_ratio:.2%} difference)"
                }
        
        return results
    
    def _get_sensor_location(self, sensor_id):
        """
        Get the location string for a sensor ID.
        
        Args:
            sensor_id (int): ID of the sensor
            
        Returns:
            str: Location string (e.g., 'tread_left', 'sidewall')
        """
        locations = {
            1: 'tread_left',
            2: 'tread_right',
            3: 'sidewall',
            4: 'bead'
        }
        return locations.get(sensor_id, 'unknown')
    
    def analyze_data(self, processed_data):
        """
        Perform full anomaly detection on processed data.
        
        Args:
            processed_data (dict): Dictionary with preprocessed sensor readings
            
        Returns:
            dict: Dictionary with comprehensive anomaly detection results
        """
        # Update history with new data
        self.update_history(processed_data)
        
        # Perform different types of anomaly detection
        threshold_results = self.detect_threshold_anomalies(processed_data)
        rate_results = self.detect_rate_anomalies(processed_data)
        trend_results = self.detect_trend_anomalies()
        
        # Combine results, prioritizing more severe anomalies
        combined_results = {
            'timestamp': processed_data['timestamp'],
            'time_step': processed_data['time_step'],
            'anomalies': {}
        }
        
        for sensor_id in threshold_results:
            # Start with threshold results
            result = threshold_results[sensor_id]
            
            # If no anomaly detected by threshold, check rate results
            if not result['anomaly_detected'] and rate_results[sensor_id]['anomaly_detected']:
                result = rate_results[sensor_id]
            
            # If still no anomaly, check trend results
            if not result['anomaly_detected'] and trend_results[sensor_id]['anomaly_detected']:
                result = trend_results[sensor_id]
            
            # Add to combined results
            combined_results['anomalies'][sensor_id] = result
        
        return combined_results


# Example usage if run directly
if __name__ == "__main__":
    # Import required modules for demonstration
    from sensor_simulation import TireImpedanceSensorArray
    from data_preprocessing import ImpedanceDataPreprocessor
    
    # Initialize components
    sensor_array = TireImpedanceSensorArray()
    preprocessor = ImpedanceDataPreprocessor(window_size=5)
    detector = TireAnomalyDetector(history_length=10)
    
    # Simulate normal operation for a while
    print("Simulating normal operation...")
    for i in range(8):
        # Collect and process data
        raw_data = sensor_array.collect_data()
        processed_data = preprocessor.preprocess_data(raw_data)
        
        # Analyze for anomalies
        results = detector.analyze_data(processed_data)
        
        # Print simplified results
        print(f"\nTime step {results['time_step']} - "
              f"Timestamp: {results['timestamp']}")
        
        anomalies_detected = False
        for sensor_id, anomaly in results['anomalies'].items():
            if anomaly['anomaly_detected']:
                anomalies_detected = True
                location = processed_data['readings'][sensor_id]['location']
                print(f"  ANOMALY DETECTED - Sensor {sensor_id} ({location}):")
                print(f"    Type: {anomaly['anomaly_type'].name}")
                print(f"    Confidence: {anomaly['confidence']:.2f}")
                print(f"    Details: {anomaly['details']}")
        
        if not anomalies_detected:
            print("  All sensors normal")
        
        time.sleep(0.5)  # Short delay for demonstration
    
    # Simulate damage
    print("\nSimulating sidewall damage...")
    sensor_array.simulate_damage(3, 'sidewall')
    
    # Simulate more readings after damage
    for i in range(5):
        # Collect and process data
        raw_data = sensor_array.collect_data()
        processed_data = preprocessor.preprocess_data(raw_data)
        
        # Analyze for anomalies
        results = detector.analyze_data(processed_data)
        
        # Print simplified results
        print(f"\nTime step {results['time_step']} - "
              f"Timestamp: {results['timestamp']}")
        
        anomalies_detected = False
        for sensor_id, anomaly in results['anomalies'].items():
            if anomaly['anomaly_detected']:
                anomalies_detected = True
                location = processed_data['readings'][sensor_id]['location']
                print(f"  ANOMALY DETECTED - Sensor {sensor_id} ({location}):")
                print(f"    Type: {anomaly['anomaly_type'].name}")
                print(f"    Confidence: {anomaly['confidence']:.2f}")
                print(f"    Details: {anomaly['details']}")
        
        if not anomalies_detected:
            print("  All sensors normal")
        
        time.sleep(0.5)  # Short delay for demonstration
