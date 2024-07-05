from labscript import start, stop
from labscriptlib.Rydberg.office_connection_table import cxn_table

if __name__ == '__main__':
    # Import and define the global variables for devices
    cxn_table()

    t = 0
    start()

    # SynthUSB3 Tests
    print("Starting SynthUSB3 tests")

    # Enable output
    synthusb3.enable_output(1)
    print("Enabling synthusb3")
    t += 1

    # Set initial frequency and power
    synthusb3.set_frequency(100)  # 100 MHz
    synthusb3.set_power(0)  # 0 dBm
    t += 1

    # Frequency changes
    for freq in [200, 300, 400, 500]:
        synthusb3.set_frequency(freq)
        t += 1

    # Power changes
    for power in [5, 10, 15, 20]:
        synthusb3.set_power(power)
        t += 1

    # Frequency sweep
    start_freq = 100.0  # MHz
    stop_freq = 500.0   # MHz
    step_size = 100.0   # MHz
    step_time = 5000    # ms
    synthusb3.set_sweep(start_freq, stop_freq, step_size, step_time)
    synthusb3.run_sweep(continuous=False)
    
    sweep_duration = (stop_freq - start_freq) / step_size * step_time / 1000  # seconds
    t += sweep_duration

    synthusb3.stop_sweep()
    t += 1

    # Rapid frequency changes
    for freq in [100, 300, 500, 200, 400]:
        synthusb3.set_frequency(freq)
        t += 0.5  # Shorter time for rapid changes

    # Disable output
    synthusb3.enable_output(0)
    t += 1

    print("SynthUSB3 tests completed")

    # KoheronCTL200 Tests
    print("Starting KoheronCTL200 tests")

    # Get initial status
    ctl200.get_status()
    t += 0.1

    # Enable laser and set current
    ctl200.enable_laser(True)
    t += 0.1
    ctl200.set_laser_current(50)  # Set current to 50 mA
    t += 0.1

    # Set temperature
    ctl200.set_temperature(10000)  # Set temperature to 10 kOhm resistance
    t += 0.1

    # Set PID gains
    ctl200.set_pid_gains(1.0, 0.1, 0.01)
    t += 0.1

    # Set current limit
    ctl200.set_current_limit(100)  # Set current limit to 100 mA
    t += 0.1

    # Enable temperature protection and set limits
    ctl200.set_temp_protection(True)
    t += 0.1
    ctl200.set_temp_limits(8000, 12000)  # Set temperature limits (in Ohms)
    t += 0.1

    # Set TEC voltage limits
    ctl200.set_tec_voltage_limits(-2.0, 2.0)  # Set TEC voltage limits
    t += 0.1

    # Get various readings
    ctl200.get_laser_current()
    t += 0.1
    ctl200.get_temperature()
    t += 0.1
    ctl200.get_tec_current()
    t += 0.1
    ctl200.get_photodiode_current()
    t += 0.1

    # Check for errors and clear if any
    ctl200.get_error()
    t += 0.1
    ctl200.clear_error()
    t += 0.1

    # Disable laser and save settings
    ctl200.enable_laser(False)
    t += 0.1
    ctl200.save_settings()
    t += 0.1

    # Final status check
    ctl200.get_status()
    t += 0.1

    print("KoheronCTL200 tests completed")

    stop(t)