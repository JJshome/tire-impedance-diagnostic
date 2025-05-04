#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tire Impedance Data Preprocessing Module
Based on Ucaretron Inc. patent application: "Tire Condition Diagnostic System and Method Using Impedance Measurement"

This module handles preprocessing of impedance data from tire sensors:
- Filtering noise from raw sensor readings
- Temperature compensation to normalize impedance values
- Moving average calculations for trend analysis
- Data normalization for anomaly detection
"""

import numpy as np
from collections import deque


class ImpedanceDataPreprocessor:
    """
    Preprocesses impedance data from tire sensors.
    
    Attributes:
        window_size (int): Size of the window for moving average calculations
        history (dict): Dictionary storing historical data for each sensor
    """
    
    def __init__(self, window_size=10):
        """
        Initialize the data preprocessor.
        
        Args:
            window_size (int): Number of readings to use for moving averages
        """
        self.window_size = window_size
        self.history = {
            1: deque(maxlen=window_size),  # Sensor 1 (tread_left)
            2: deque(maxlen=window_size),  # Sensor 2 (tread_right)
            3: deque(maxlen=window_size),  # Sensor 3 (sidewall)
            4: deque(maxlen=window_size)   # Sensor 4 (bead)
        }
        
        # Store base impedance values for each sensor location
        self.base_impedance = {
            1: 100.0,  # tread_left
            2: 100.0,  # tread_right
            3: 120.0,  # sidewall
            4: 150.0   # bead
        }
        
        # Store reference temperature
        self.reference_temp = 25.0  # 25°C is the reference temperature
        
    def filter_noise(self, reading):
        """
        Apply a simple low-pass filter to raw impedance readings.
        This simulates the application of a Butterworth filter mentioned in the patent.
        
        Args:
            reading (float): Raw impedance reading
            
        Returns:
            float: Filtered impedance reading
        """
        # Simple low-pass filter implementation
        # In a real system, a proper Butterworth filter would be used
        filtered_reading = reading  # For demonstration, minimal filtering is applied
        return filtered_reading
        
    def temperature_compensation(self, reading, temperature):
        """
        Compensate for temperature effects on impedance readings.
        As mentioned in the patent, temperature changes can affect impedance values.
        
        Args:
            reading (float): Impedance reading to compensate
            temperature (float): Current temperature in Celsius
            
        Returns:
            float: Temperature-compensated impedance reading
        """
        # Calculate compensation factor
        # Impedance increases with temperature, so normalize to reference temperature
        temp_diff = temperature - self.reference_temp
        compensation_factor = 1.0 / (1.0 + (temp_diff * 0.001))
        
        # Apply compensation
        compensated_reading = reading * compensation_factor
        return compensated_reading
        
    def calculate_moving_average(self, sensor_id, reading):
        """
        Calculate moving average for a sensor's readings.
        
        Args:
            sensor_id (int): ID of the sensor
            reading (float): Current preprocessed reading
            
        Returns:
            float: Moving average of recent readings
        """
        # Add reading to history
        self.history[sensor_id].append(reading)
        
        # Calculate moving average if enough data points
        if len(self.history[sensor_id]) > 0:
            return sum(self.history[sensor_id]) / len(self.history[sensor_id])
        else:
            return reading
    
    def normalize_reading(self, sensor_id, reading):
        """
        Normalize reading against baseline impedance for this sensor.
        This helps in comparing values across different sensor locations.
        
        Args:
            sensor_id (int): ID of the sensor
            reading (float): Preprocessed impedance reading
            
        Returns:
            float: Normalized impedance value (ratio to baseline)
        """
        return reading / self.base_impedance[sensor_id]
    
    def preprocess_data(self, sensor_data):
        """
        Apply full preprocessing pipeline to sensor data.
        
        Args:
            sensor_data (dict): Dictionary with readings from all sensors
            
        Returns:
            dict: Dictionary with preprocessed readings
        """
        processed_data = {
            'timestamp': sensor_data['timestamp'],
            'time_step': sensor_data['time_step'],
            'readings': {}
        }
        
        for sensor_id, reading_info in sensor_data['readings'].items():
            # Get raw data
            raw_value = reading_info['value']
            temperature = reading_info['temperature']
            
            # Apply preprocessing steps
            filtered_value = self.filter_noise(raw_value)
            compensated_value = self.temperature_compensation(filtered_value, temperature)
            moving_avg = self.calculate_moving_average(sensor_id, compensated_value)
            normalized_value = self.normalize_reading(sensor_id, moving_avg)
            
            # Store processed data
            processed_data['readings'][sensor_id] = {
                'raw_value': raw_value,
                'filtered_value': filtered_value,
                'compensated_value': compensated_value,
                'moving_avg': moving_avg,
                'normalized_value': normalized_value,
                'location': reading_info['location'],
                'temperature': temperature
            }
            
        return processed_data


# Example usage when run directly
if __name__ == "__main__":
    # Import sensor simulation for demonstration
    from sensor_simulation import TireImpedanceSensorArray
    import time
    
    # Initialize sensor array and preprocessor
    sensor_array = TireImpedanceSensorArray()
    preprocessor = ImpedanceDataPreprocessor(window_size=5)
    
    # Collect and process data for a few time steps
    for _ in range(8):
        # Collect raw data
        raw_data = sensor_array.collect_data()
        
        # Preprocess data
        processed_data = preprocessor.preprocess_data(raw_data)
        
        # Print results
        print(f"\nTime step {processed_data['time_step']} - "
              f"Timestamp: {processed_data['timestamp']}")
        
        for sensor_id, reading in processed_data['readings'].items():
            print(f"  Sensor {sensor_id} ({reading['location']}):")
            print(f"    Raw value: {reading['raw_value']:.2f} ohms")
            print(f"    Filtered value: {reading['filtered_value']:.2f} ohms")
            print(f"    Temp-compensated: {reading['compensated_value']:.2f} ohms")
            print(f"    Moving average: {reading['moving_avg']:.2f} ohms")
            print(f"    Normalized value: {reading['normalized_value']:.2f}")
            print(f"    Temperature: {reading['temperature']:.1f}°C")
        
        time.sleep(1)  # Short delay for demonstration
    
    # Simulate damage and see the preprocessing results
    print("\nSimulating sidewall damage...")
    sensor_array.simulate_damage(3, 'sidewall')
    
    for _ in range(3):
        raw_data = sensor_array.collect_data()
        processed_data = preprocessor.preprocess_data(raw_data)
        
        print(f"\nTime step {processed_data['time_step']} - "
              f"Timestamp: {processed_data['timestamp']}")
        
        for sensor_id, reading in processed_data['readings'].items():
            print(f"  Sensor {sensor_id} ({reading['location']}):")
            print(f"    Raw value: {reading['raw_value']:.2f} ohms")
            print(f"    Moving average: {reading['moving_avg']:.2f} ohms")
            print(f"    Normalized value: {reading['normalized_value']:.2f}")
        
        time.sleep(1)
