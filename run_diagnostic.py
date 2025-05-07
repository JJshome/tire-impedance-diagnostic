#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tire Impedance Diagnostic System - Complete Workflow
Based on Ucaretron Inc. patent application: "Tire Condition Diagnostic System and Method Using Impedance Measurement"

This script provides a user-friendly interface to run the complete diagnostic workflow:
1. Generate simulation data for various tire conditions
2. Process and analyze the data
3. Detect anomalies and generate alerts
4. Visualize results and create diagnostic reports

Usage: python run_diagnostic.py [options]
"""

import os
import sys
import time
import argparse
from datetime import datetime
import subprocess

def print_header():
    """Print a header with ASCII art of a tire and the system title."""
    header = """
    ╭───────────────────────────────────────────────────────╮
    │                                                       │
    │   ████████╗██╗██████╗ ███████╗    ██████╗ ██╗ █████╗  │
    │   ╚══██╔══╝██║██╔══██╗██╔════╝    ██╔══██╗██║██╔══██╗ │
    │      ██║   ██║██████╔╝█████╗      ██║  ██║██║███████║ │
    │      ██║   ██║██╔══██╗██╔══╝      ██║  ██║██║██╔══██║ │
    │      ██║   ██║██║  ██║███████╗    ██████╔╝██║██║  ██║ │
    │      ╚═╝   ╚═╝╚═╝  ╚═╝╚══════╝    ╚═════╝ ╚═╝╚═╝  ╚═╝ │
    │                                                       │
    │       TIRE CONDITION DIAGNOSTIC SYSTEM                │
    │         USING IMPEDANCE MEASUREMENT                   │
    │                                                       │
    │       Based on Ucaretron Inc. Patent Application      │
    │                                                       │
    ╰───────────────────────────────────────────────────────╯
    """
    print(header)

def check_requirements():
    """Check if required packages are installed."""
    try:
        import numpy
        import pandas
        import matplotlib
        import sklearn
        print("✅ All required packages are installed.")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install the required packages using:")
        print("  pip install -r requirements.txt")
        return False

def create_directories():
    """Create necessary directories for data and output."""
    if not os.path.exists('data'):
        os.makedirs('data')
        print("✅ Created 'data' directory.")
    
    if not os.path.exists('output'):
        os.makedirs('output')
        print("✅ Created 'output' directory.")

def wait_with_animation(seconds, message="Processing"):
    """Display a waiting animation for the specified number of seconds."""
    animation = "|/-\\"
    for i in range(seconds * 10):
        time.sleep(0.1)
        sys.stdout.write(f"\r{message} {animation[i % len(animation)]}")
        sys.stdout.flush()
    sys.stdout.write("\r" + " " * (len(message) + 2) + "\r")
    sys.stdout.flush()

def run_command(command, shell=False):
    """Run a command and return its output."""
    try:
        result = subprocess.run(command, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True,
                               shell=shell)
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1

def generate_data(scenario, time_steps=300, damage_time=100, interval=30):
    """Generate simulation data for a specific scenario."""
    print(f"\n📊 Generating simulation data for {scenario} scenario...")
    
    command = [
        "python", "generate_simulation_data.py",
        "--scenario", scenario,
        "--time-steps", str(time_steps),
        "--damage-time", str(damage_time),
        "--interval", str(interval)
    ]
    
    stdout, stderr, returncode = run_command(command)
    
    if returncode == 0:
        print(f"✅ Successfully generated data for {scenario} scenario.")
        return True
    else:
        print(f"❌ Error generating data for {scenario} scenario:")
        print(stderr)
        return False

def analyze_data(data_file=None):
    """Analyze the generated data."""
    print("\n🔍 Analyzing simulation data...")
    
    if data_file:
        command = ["python", "analyze_simulation_data.py", "--file", data_file]
    else:
        command = ["python", "analyze_simulation_data.py", "--latest"]
    
    stdout, stderr, returncode = run_command(command)
    
    if returncode == 0:
        print("✅ Successfully analyzed data.")
        return True
    else:
        print("❌ Error analyzing data:")
        print(stderr)
        return False

def run_full_simulation():
    """Run the full tire diagnostic simulator using real-time simulation."""
    print("\n🔄 Running full real-time tire diagnostic simulation...")
    
    command = [
        "python", "tire_diagnostic_system.py",
        "--interval", "2",      # 2 seconds between readings for faster demo
        "--duration", "30",     # 30 seconds total simulation
        "--damage-time", "15"   # Damage occurs at 15 seconds
    ]
    
    print("\nStarting simulation in 3 seconds...")
    wait_with_animation(3, "Starting")
    
    process = subprocess.Popen(command)
    process.wait()
    
    if process.returncode == 0:
        print("✅ Full simulation completed successfully.")
        return True
    else:
        print("❌ Error during simulation.")
        return False

def open_output_file(file_path):
    """Open a file with the default application."""
    import platform
    import subprocess
    
    try:
        if platform.system() == 'Darwin':  # macOS
            subprocess.run(['open', file_path])
        elif platform.system() == 'Windows':  # Windows
            os.startfile(file_path)
        else:  # Linux
            subprocess.run(['xdg-open', file_path])
        return True
    except Exception as e:
        print(f"Error opening file: {e}")
        return False

def show_latest_results():
    """Show the latest results from the output directory."""
    print("\n📋 Latest Analysis Results:")
    
    # Find latest report file
    report_files = [f for f in os.listdir('output') if f.startswith('tire_diagnostic_report_')]
    
    if report_files:
        latest_report = max(report_files, key=lambda f: os.path.getmtime(os.path.join('output', f)))
        print(f"  - Latest report: {latest_report}")
        
        # Read and show summary of report
        with open(os.path.join('output', latest_report), 'r') as f:
            report_content = f.read()
            # Show first 15 lines
            print("\nReport Summary:")
            print("\n".join(report_content.split('\n')[:15]))
            print("...")
        
        # Ask if user wants to open the full report
        user_input = input("\nDo you want to open the full report? (y/n): ")
        if user_input.lower() == 'y':
            open_output_file(os.path.join('output', latest_report))
    else:
        print("  No report files found in output directory.")
    
    # Find latest visualization files
    visualization_files = [f for f in os.listdir('output') if f.endswith('.png')]
    
    if visualization_files:
        impedance_plots = [f for f in visualization_files if 'impedance' in f]
        status_plots = [f for f in visualization_files if 'tire_status' in f]
        
        if impedance_plots:
            latest_plot = max(impedance_plots, key=lambda f: os.path.getmtime(os.path.join('output', f)))
            print(f"\n  - Latest impedance plot: {latest_plot}")
            user_input = input("\nDo you want to open the impedance plot? (y/n): ")
            if user_input.lower() == 'y':
                open_output_file(os.path.join('output', latest_plot))
        
        if status_plots:
            latest_status = max(status_plots, key=lambda f: os.path.getmtime(os.path.join('output', f)))
            print(f"\n  - Latest tire status visualization: {latest_status}")
            user_input = input("\nDo you want to open the tire status visualization? (y/n): ")
            if user_input.lower() == 'y':
                open_output_file(os.path.join('output', latest_status))
    else:
        print("  No visualization files found in output directory.")

def show_menu():
    """Display the main menu and handle user selection."""
    while True:
        print("\n" + "=" * 60)
        print("TIRE DIAGNOSTIC SYSTEM - MAIN MENU")
        print("=" * 60)
        print("1. Generate Data for a Specific Scenario")
        print("2. Generate Data for All Scenarios")
        print("3. Analyze Latest Generated Data")
        print("4. Run Full Real-Time Diagnostic Simulation")
        print("5. View Latest Results")
        print("0. Exit")
        print("-" * 60)
        
        choice = input("Enter your choice (0-5): ")
        
        if choice == '0':
            print("\nExiting the Tire Diagnostic System. Thank you!")
            break
        
        elif choice == '1':
            print("\nAvailable scenarios:")
            print("  1. normal - Normal tire operation")
            print("  2. gradual_wear - Tire with gradual wear")
            print("  3. sidewall_damage - Tire with sidewall damage")
            print("  4. tread_damage - Tire with tread damage")
            print("  5. puncture - Tire with puncture")
            
            scenario_choice = input("\nSelect scenario (1-5): ")
            scenarios = ["normal", "gradual_wear", "sidewall_damage", "tread_damage", "puncture"]
            
            if scenario_choice in ['1', '2', '3', '4', '5']:
                scenario = scenarios[int(scenario_choice) - 1]
                time_steps = int(input("Enter number of time steps (default 300): ") or "300")
                damage_time = int(input("Enter damage time step (default 100): ") or "100")
                interval = int(input("Enter time interval in seconds (default 30): ") or "30")
                
                generate_data(scenario, time_steps, damage_time, interval)
                
                analyze_choice = input("\nAnalyze this data now? (y/n): ")
                if analyze_choice.lower() == 'y':
                    analyze_data()
            else:
                print("Invalid scenario choice.")
        
        elif choice == '2':
            print("\nGenerating data for all scenarios...")
            time_steps = int(input("Enter number of time steps (default 300): ") or "300")
            damage_time = int(input("Enter damage time step (default 100): ") or "100")
            interval = int(input("Enter time interval in seconds (default 30): ") or "30")
            
            scenarios = ["normal", "gradual_wear", "sidewall_damage", "tread_damage", "puncture"]
            
            for scenario in scenarios:
                generate_data(scenario, time_steps, damage_time, interval)
                wait_with_animation(1, "Processing")
            
            analyze_choice = input("\nAnalyze the latest generated data now? (y/n): ")
            if analyze_choice.lower() == 'y':
                analyze_data()
        
        elif choice == '3':
            print("\nAnalyzing latest generated data...")
            analyze_data()
        
        elif choice == '4':
            print("\nRunning full real-time diagnostic simulation...")
            damage_type = input("Enter damage type (sidewall, tread, puncture, wear) [default: sidewall]: ") or "sidewall"
            
            command = [
                "python", "tire_diagnostic_system.py",
                "--interval", "2",      # 2 seconds between readings for faster demo
                "--duration", "30",     # 30 seconds total simulation
                "--damage-time", "15",  # Damage occurs at 15 seconds
                "--damage-type", damage_type
            ]
            
            print("\nStarting simulation in 3 seconds...")
            wait_with_animation(3, "Starting")
            
            process = subprocess.Popen(command)
            process.wait()
            
            print("\nSimulation completed.")
        
        elif choice == '5':
            show_latest_results()
        
        else:
            print("Invalid choice. Please try again.")

def main():
    """Main function to run the tire diagnostic workflow."""
    parser = argparse.ArgumentParser(
        description='Tire Impedance Diagnostic System')
    
    parser.add_argument('--scenario', type=str,
                        choices=['normal', 'gradual_wear', 'sidewall_damage', 
                                'tread_damage', 'puncture', 'all'],
                        help='Scenario to generate data for')
    parser.add_argument('--analyze', action='store_true',
                        help='Analyze the generated data')
    parser.add_argument('--simulate', action='store_true',
                        help='Run the full simulation')
    parser.add_argument('--menu', action='store_true',
                        help='Show the interactive menu')
    
    args = parser.parse_args()
    
    # Print header
    print_header()
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Create necessary directories
    create_directories()
    
    # Interactive mode if no arguments or --menu is specified
    if len(sys.argv) == 1 or args.menu:
        show_menu()
        return
    
    # Generate data if scenario is specified
    if args.scenario:
        if args.scenario == 'all':
            scenarios = ["normal", "gradual_wear", "sidewall_damage", "tread_damage", "puncture"]
            for scenario in scenarios:
                generate_data(scenario)
                wait_with_animation(1, "Processing")
        else:
            generate_data(args.scenario)
    
    # Analyze data if --analyze is specified
    if args.analyze:
        analyze_data()
    
    # Run simulation if --simulate is specified
    if args.simulate:
        run_full_simulation()


if __name__ == "__main__":
    main()
