#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tire Impedance Simulation Data Generator
Based on Ucaretron Inc. patent application: "Tire Condition Diagnostic System and Method Using Impedance Measurement"

This script generates simulation data for different tire conditions:
- Normal operation
- Gradual wear
- Sidewall damage
- Tread damage
- Puncture

The generated data is saved to CSV files for later analysis and visualization.
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
import argparse

class TireImpedanceDataGenerator:
    """
    Generates simulated impedance data for tire sensors.
    
    Attributes:
        sensor_count (int): Number of sensors to simulate
        base_impedance (dict): Base impedance values for each sensor
        damage_scenarios (dict): Different damage scenarios to simulate
    """
    
    def __init__(self, sensor_count=4):
        """
        Initialize the data generator.
        
        Args:
            sensor_count (int): Number of sensors to simulate
        """
        self.sensor_count = sensor_count
        
        # Base impedance values for different sensors
        self.base_impedance = {
            1: 100.0,  # Tread left
            2: 100.0,  # Tread right
            3: 120.0,  # Sidewall
            4: 150.0   # Bead
        }
        
        # Sensor locations
        self.sensor_locations = {
            1: 'tread_left',
            2: 'tread_right',
            3: 'sidewall',
            4: 'bead'
        }
        
        # Define damage scenarios
        self.damage_scenarios = {
            'normal': {
                'wear_rate': 0.0001,
                'noise_level': 0.02,
                'affected_sensors': []
            },
            'gradual_wear': {
                'wear_rate': 0.0003,
                'noise_level': 0.02,
                'affected_sensors': [1, 2]
            },
            'sidewall_damage': {
                'wear_rate': 0.0001,
                'noise_level': 0.05,
                'affected_sensors': [3],
                'damage_factor': 1.5
            },
            'tread_damage': {
                'wear_rate': 0.0001,
                'noise_level': 0.03,
                'affected_sensors': [1],
                'damage_factor': 1.3
            },
            'puncture': {
                'wear_rate': 0.0001,
                'noise_level': 0.08,
                'affected_sensors': [1, 2],
                'damage_factor': 2.0
            }
        }
    
    def generate_temperature(self, time_step, base_temp=25.0, amplitude=5.0, period=100):
        """
        Generate a simulated temperature value with realistic fluctuations.
        
        Args:
            time_step (int): Current time step
            base_temp (float): Base temperature in Celsius
            amplitude (float): Amplitude of temperature fluctuations
            period (int): Period of temperature cycle
            
        Returns:
            float: Simulated temperature value
        """
        # Simulate temperature variations using sine wave + noise
        cycle_position = time_step % period
        sinusoidal = np.sin(2 * np.pi * cycle_position / period)
        
        # Add small random noise
        noise = random.normalvariate(0, 0.5)
        
        # Calculate temperature
        temperature = base_temp + amplitude * sinusoidal + noise
        
        return temperature
    
    def generate_impedance(self, sensor_id, time_step, scenario='normal', damage_time=None):
        """
        Generate a simulated impedance reading for a sensor.
        
        Args:
            sensor_id (int): ID of the sensor
            time_step (int): Current time step
            scenario (str): Damage scenario to simulate
            damage_time (int, optional): Time step when damage occurs
            
        Returns:
            tuple: (impedance, temperature)
        """
        # Get base values for this sensor
        base_value = self.base_impedance[sensor_id]
        
        # Get scenario parameters
        wear_rate = self.damage_scenarios[scenario]['wear_rate']
        noise_level = self.damage_scenarios[scenario]['noise_level']
        affected_sensors = self.damage_scenarios[scenario]['affected_sensors']
        
        # Calculate wear factor based on time
        wear_factor = 1.0 + (time_step * wear_rate)
        
        # Generate temperature
        temperature = self.generate_temperature(time_step)
        
        # Temperature effect on impedance (impedance increases with temperature)
        temp_effect = 1.0 + (temperature - 25) * 0.001
        
        # Calculate impedance with wear and temperature effects
        impedance = base_value * wear_factor * temp_effect
        
        # Add damage effect if applicable
        if (damage_time is not None and time_step >= damage_time and 
                sensor_id in affected_sensors and scenario != 'normal'):
            
            damage_factor = self.damage_scenarios[scenario].get('damage_factor', 1.0)
            time_since_damage = time_step - damage_time
            
            # Gradual increase in damage effect
            if time_since_damage < 10:
                damage_effect = 1.0 + (damage_factor - 1.0) * (time_since_damage / 10)
            else:
                damage_effect = damage_factor
                
            impedance *= damage_effect
        
        # Add noise
        noise = random.normalvariate(0, noise_level * base_value)
        impedance += noise
        
        return impedance, temperature
    
    def generate_dataset(self, time_steps=300, scenario='normal', damage_time=None, 
                        interval_seconds=30, output_dir='data'):
        """
        Generate a full dataset of simulated impedance readings.
        
        Args:
            time_steps (int): Number of time steps to generate
            scenario (str): Damage scenario to simulate
            damage_time (int, optional): Time step when damage occurs
            interval_seconds (int): Time interval between readings in seconds
            output_dir (str): Directory to save output data
            
        Returns:
            pandas.DataFrame: DataFrame with generated data
        """
        # Create data structure
        data = {
            'timestamp': [],
            'time_step': []
        }
        
        # Add columns for each sensor
        for sensor_id in range(1, self.sensor_count + 1):
            data[f'sensor_{sensor_id}_impedance'] = []
            data[f'sensor_{sensor_id}_temperature'] = []
            data[f'sensor_{sensor_id}_location'] = []
        
        # Generate data for each time step
        start_time = datetime.now()
        
        for time_step in range(time_steps):
            # Current timestamp
            current_time = start_time + timedelta(seconds=time_step * interval_seconds)
            
            # Add time step data
            data['timestamp'].append(current_time)
            data['time_step'].append(time_step)
            
            # Generate data for each sensor
            for sensor_id in range(1, self.sensor_count + 1):
                impedance, temperature = self.generate_impedance(
                    sensor_id, time_step, scenario, damage_time)
                
                data[f'sensor_{sensor_id}_impedance'].append(impedance)
                data[f'sensor_{sensor_id}_temperature'].append(temperature)
                data[f'sensor_{sensor_id}_location'].append(self.sensor_locations[sensor_id])
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Save to CSV
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{output_dir}/{scenario}_data_{timestamp_str}.csv"
        df.to_csv(filename, index=False)
        
        print(f"Generated {time_steps} data points for scenario '{scenario}'")
        print(f"Data saved to: {filename}")
        
        return df
    
    def generate_all_scenarios(self, time_steps=300, damage_time=100, 
                              interval_seconds=30, output_dir='data'):
        """
        Generate datasets for all damage scenarios.
        
        Args:
            time_steps (int): Number of time steps to generate
            damage_time (int): Time step when damage occurs
            interval_seconds (int): Time interval between readings in seconds
            output_dir (str): Directory to save output data
            
        Returns:
            dict: Dictionary with generated DataFrames for each scenario
        """
        datasets = {}
        
        for scenario in self.damage_scenarios.keys():
            print(f"\nGenerating data for scenario: {scenario}")
            
            # For normal scenario, no damage time needed
            dt = None if scenario == 'normal' else damage_time
            
            df = self.generate_dataset(
                time_steps=time_steps,
                scenario=scenario,
                damage_time=dt,
                interval_seconds=interval_seconds,
                output_dir=output_dir
            )
            
            datasets[scenario] = df
        
        return datasets


def main():
    """Main function to generate simulation data."""
    parser = argparse.ArgumentParser(
        description='Generate simulated tire impedance data for different scenarios')
    
    parser.add_argument('--time-steps', type=int, default=300,
                        help='Number of time steps to generate (default: 300)')
    parser.add_argument('--damage-time', type=int, default=100,
                        help='Time step when damage occurs (default: 100)')
    parser.add_argument('--interval', type=int, default=30,
                        help='Time interval between readings in seconds (default: 30)')
    parser.add_argument('--output-dir', type=str, default='data',
                        help='Directory to save output data (default: data)')
    parser.add_argument('--scenario', type=str, default='all',
                        choices=['all', 'normal', 'gradual_wear', 'sidewall_damage', 
                                'tread_damage', 'puncture'],
                        help='Scenario to generate data for (default: all)')
    
    args = parser.parse_args()
    
    # Initialize data generator
    generator = TireImpedanceDataGenerator()
    
    # Generate data
    if args.scenario == 'all':
        generator.generate_all_scenarios(
            time_steps=args.time_steps,
            damage_time=args.damage_time,
            interval_seconds=args.interval,
            output_dir=args.output_dir
        )
    else:
        generator.generate_dataset(
            time_steps=args.time_steps,
            scenario=args.scenario,
            damage_time=args.damage_time if args.scenario != 'normal' else None,
            interval_seconds=args.interval,
            output_dir=args.output_dir
        )


if __name__ == "__main__":
    print("=" * 80)
    print("Tire Impedance Simulation Data Generator")
    print("Based on Ucaretron Inc. patent application")
    print("=" * 80)
    print("\nUSAGE EXAMPLES:")
    print("  python generate_simulation_data.py")
    print("  python generate_simulation_data.py --scenario sidewall_damage --time-steps 200")
    print("  python generate_simulation_data.py --damage-time 50 --interval 10")
    print("-" * 80)
    
    main()
