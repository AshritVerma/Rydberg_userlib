from labscript import start, stop
from labscriptlib.Rydberg.office_connection_table import cxn_table

if __name__ == '__main__':
    # Import and define the global variables for devices
    cxn_table()

    t = 0
    start()

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

    stop(t)