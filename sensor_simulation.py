#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tire Impedance Sensor Simulation Module
Based on Ucaretron Inc. patent application: "Tire Condition Diagnostic System and Method Using Impedance Measurement"

This module simulates 4 impedance sensors placed in different locations of a tire:
- Sensor 1: Tread (left)
- Sensor 2: Tread (right)
- Sensor 3: Sidewall
- Sensor 4: Bead area

Each sensor measures impedance values at 30-second intervals.
"""

import time
import random
import numpy as np
from datetime import datetime

class TireImpedanceSensor:
    """
    Simulates an impedance sensor placed within a tire.
    
    Attributes:
        sensor_id (int): Unique identifier for the sensor
        location (str): Location within the tire (tread, sidewall, bead)
        base_impedance (float): Base impedance value for this sensor location
        noise_level (float): Amount of random noise to add to readings
        wear_rate (float): Rate at which impedance increases due to wear
        temperature (float): Current temperature affecting the sensor
        wear_factor (float): Current wear factor affecting impedance
        damage_flag (bool): Flag to indicate if damage simulation is active
    """
    
    def __init__(self, sensor_id, location, base_impedance, noise_level=0.05):
        """
        Initialize a tire impedance sensor.
        
        Args:
            sensor_id (int): Unique identifier for the sensor
            location (str): Location within the tire (tread, sidewall, bead)
            base_impedance (float): Base impedance value for this sensor location
            noise_level (float): Amount of random noise to add to readings
        """
        self.sensor_id = sensor_id
        self.location = location
        self.base_impedance = base_impedance
        self.noise_level = noise_level
        self.wear_rate = 0.0001  # Small increment per reading
        self.temperature = 25.0  # Starting temperature in Celsius
        self.wear_factor = 1.0   # Start with no wear
        self.damage_flag = False
        
        # Readings history
        self.history = []
        self.timestamps = []
        
    def get_impedance_reading(self, time_step):
        """
        Generate a simulated impedance reading.
        
        Args:
            time_step (int): Current time step of the simulation
            
        Returns:
            float: Simulated impedance reading
        """
        # Update wear factor (gradual increase over time)
        self.wear_factor += self.wear_rate
        
        # Update temperature (simulate temperature fluctuation)
        self.temperature += random.normalvariate(0, 0.5)
        self.temperature = max(10, min(80, self.temperature))  # Keep in reasonable range
        
        # Calculate temperature effect (impedance increases with temperature)
        temp_effect = 1.0 + (self.temperature - 25) * 0.001
        
        # Calculate base reading with wear factor
        reading = self.base_impedance * self.wear_factor * temp_effect
        
        # Add random noise
        noise = random.normalvariate(0, self.noise_level * self.base_impedance)
        reading += noise
        
        # Simulate damage if flag is set
        if self.damage_flag:
            if self.location == 'sidewall':
                # Simulate sidewall damage with a sharp increase
                reading *= 1.5
            elif self.location == 'tread':
                # Simulate tread damage with a moderate increase
                reading *= 1.2
        
        # Store reading in history
        self.history.append(reading)
        self.timestamps.append(datetime.now())
        
        return reading
    
    def simulate_damage(self, damage_type=None):
        """
        Simulate damage to the tire at this sensor's location.
        
        Args:
            damage_type (str, optional): Type of damage to simulate
                                        ('wear', 'puncture', 'sidewall')
        """
        self.damage_flag = True
        if damage_type == 'wear':
            # Accelerate wear rate
            self.wear_rate *= 5
        elif damage_type == 'puncture':
            # Sharp increase in impedance
            self.wear_factor *= 1.3
        elif damage_type == 'sidewall':
            # Major change for sidewall damage
            if self.location == 'sidewall':
                self.wear_factor *= 1.8
        else:
            # Generic damage
            self.wear_factor *= 1.2


class TireImpedanceSensorArray:
    """
    Manages a set of tire impedance sensors and collects data from all of them.
    
    Attributes:
        sensors (list): List of TireImpedanceSensor objects
    """
    
    def __init__(self):
        """Initialize a tire impedance sensor array with 4 sensors."""
        self.sensors = [
            TireImpedanceSensor(1, 'tread_left', 100.0, 0.03),    # Tread left
            TireImpedanceSensor(2, 'tread_right', 100.0, 0.03),   # Tread right
            TireImpedanceSensor(3, 'sidewall', 120.0, 0.05),      # Sidewall
            TireImpedanceSensor(4, 'bead', 150.0, 0.02)           # Bead area
        ]
        self.time_step = 0
        
    def collect_data(self):
        """
        Collect impedance readings from all sensors.
        
        Returns:
            dict: Dictionary containing readings from all sensors
        """
        self.time_step += 1
        
        data = {
            'timestamp': datetime.now(),
            'time_step': self.time_step,
            'readings': {}
        }
        
        for sensor in self.sensors:
            reading = sensor.get_impedance_reading(self.time_step)
            data['readings'][sensor.sensor_id] = {
                'value': reading,
                'location': sensor.location,
                'temperature': sensor.temperature
            }
            
        return data
    
    def simulate_wear_over_time(self, num_steps):
        """
        Simulate tire wear over a number of time steps.
        
        Args:
            num_steps (int): Number of time steps to simulate
            
        Returns:
            list: List of data points collected
        """
        data_points = []
        
        for _ in range(num_steps):
            data = self.collect_data()
            data_points.append(data)
            
        return data_points
    
    def simulate_damage(self, sensor_id, damage_type=None):
        """
        Simulate damage to a specific sensor.
        
        Args:
            sensor_id (int): ID of the sensor to damage
            damage_type (str, optional): Type of damage to simulate
        """
        for sensor in self.sensors:
            if sensor.sensor_id == sensor_id:
                sensor.simulate_damage(damage_type)
                break


# Example usage if run directly
if __name__ == "__main__":
    # Initialize sensor array
    sensor_array = TireImpedanceSensorArray()
    
    # Collect data for 5 time steps
    for _ in range(5):
        data = sensor_array.collect_data()
        print(f"Time step {data['time_step']} - Timestamp: {data['timestamp']}")
        for sensor_id, reading in data['readings'].items():
            print(f"  Sensor {sensor_id} ({reading['location']}): "
                  f"Impedance = {reading['value']:.2f} ohms, "
                  f"Temperature = {reading['temperature']:.1f}°C")
        
        # Simulate 30-second intervals between readings
        time.sleep(1)  # Changed to 1 second for demonstration
    
    # Simulate damage to sensor 3 (sidewall)
    print("\nSimulating sidewall damage...")
    sensor_array.simulate_damage(3, 'sidewall')
    
    # Collect more data after damage
    for _ in range(5):
        data = sensor_array.collect_data()
        print(f"Time step {data['time_step']} - Timestamp: {data['timestamp']}")
        for sensor_id, reading in data['readings'].items():
            print(f"  Sensor {sensor_id} ({reading['location']}): "
                  f"Impedance = {reading['value']:.2f} ohms, "
                  f"Temperature = {reading['temperature']:.1f}°C")
        
        time.sleep(1)  # Changed to 1 second for demonstration
