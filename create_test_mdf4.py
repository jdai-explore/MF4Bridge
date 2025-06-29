#!/usr/bin/env python3
"""
Create a test MDF4 file for testing MF4Bridge functionality
"""

import os
import numpy as np
from datetime import datetime

def create_test_mdf4_file(filename: str = "test_can_data.mf4"):
    """Create a simple test MDF4 file with CAN data"""
    try:
        from asammdf import MDF, Signal
        
        print(f"Creating test MDF4 file: {filename}")
        
        # Create time base (1000 samples at 100Hz = 10 seconds)
        timestamps = np.linspace(0, 10, 1000)
        
        # Create some realistic CAN-like signals
        signals = []
        
        # Engine RPM signal (0x100)
        engine_rpm = 800 + 200 * np.sin(2 * np.pi * 0.1 * timestamps) + np.random.normal(0, 10, len(timestamps))
        engine_rpm = np.clip(engine_rpm, 600, 1200).astype(np.uint16)
        
        signal_rpm = Signal(
            samples=engine_rpm,
            timestamps=timestamps,
            name='CAN_EngineRPM',
            unit='rpm'
        )
        signals.append(signal_rpm)
        
        # Vehicle speed signal (0x200)
        vehicle_speed = 50 + 20 * np.sin(2 * np.pi * 0.05 * timestamps) + np.random.normal(0, 2, len(timestamps))
        vehicle_speed = np.clip(vehicle_speed, 0, 120).astype(np.uint8)
        
        signal_speed = Signal(
            samples=vehicle_speed,
            timestamps=timestamps,
            name='CAN_VehicleSpeed',
            unit='km/h'
        )
        signals.append(signal_speed)
        
        # Throttle position signal (0x300)
        throttle_pos = 20 + 30 * np.sin(2 * np.pi * 0.2 * timestamps) + np.random.normal(0, 1, len(timestamps))
        throttle_pos = np.clip(throttle_pos, 0, 100).astype(np.uint8)
        
        signal_throttle = Signal(
            samples=throttle_pos,
            timestamps=timestamps,
            name='CAN_ThrottlePos',
            unit='%'
        )
        signals.append(signal_throttle)
        
        # Brake pressure signal (0x400)
        brake_pressure = np.where(vehicle_speed < 30, 
                                np.random.exponential(20, len(timestamps)), 
                                np.random.exponential(5, len(timestamps)))
        brake_pressure = np.clip(brake_pressure, 0, 100).astype(np.uint8)
        
        signal_brake = Signal(
            samples=brake_pressure,
            timestamps=timestamps,
            name='CAN_BrakePressure',
            unit='bar'
        )
        signals.append(signal_brake)
        
        # Create MDF file
        with MDF(version='4.10') as mdf:
            # Add all signals to the MDF
            for signal in signals:
                mdf.append(signal)
            
            # Save the file
            mdf.save(filename)
        
        print(f"✓ Created test MDF4 file: {filename}")
        print(f"  File size: {os.path.getsize(filename)} bytes")
        print(f"  Signals: {len(signals)}")
        print(f"  Duration: {timestamps[-1]:.1f} seconds")
        print(f"  Sample rate: {len(timestamps)/timestamps[-1]:.1f} Hz")
        
        return True
        
    except ImportError:
        print("✗ asammdf not available - cannot create test MDF4 file")
        print("  Creating dummy file for testing...")
        
        # Create a dummy file with MDF4-like header
        with open(filename, 'wb') as f:
            # Write a basic MDF4 header
            f.write(b'MDF     ')  # ID block
            f.write(b'4.10')     # Version
            f.write(b'\x00' * 56)  # Padding to minimum size
            
        print(f"✓ Created dummy MDF4 file: {filename}")
        return True
        
    except Exception as e:
        print(f"✗ Error creating test file: {e}")
        return False

def main():
    """Main function"""
    print("MF4Bridge Test Data Creator")
    print("=" * 40)
    
    # Create test files
    test_files = [
        "test_can_data.mf4",
        "sample_vehicle_data.mf4",
        "demo_bus_messages.mf4"
    ]
    
    success_count = 0
    for filename in test_files:
        if create_test_mdf4_file(filename):
            success_count += 1
        print()
    
    print(f"Created {success_count}/{len(test_files)} test files")
    
    if success_count > 0:
        print("\nYou can now test MF4Bridge with these files:")
        print("python main.py")

if __name__ == "__main__":
    main()