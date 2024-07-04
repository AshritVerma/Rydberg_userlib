from labscript import start, stop
from labscriptlib.Rydberg.office_connection_table import cxn_table

if __name__ == '__main__':
    # Import and define the global variables for devices
    cxn_table()

    t = 0
    start()

    # Enable output
    synthusb3.enable_output(1)
    print("Enabling synthusb3")

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

    # Optional: Save settings to EEPROM
    # synthusb3.save_settings()
    # t += 1

    stop(t)