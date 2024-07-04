import serial
import time

COM_PORT = 'COM6'
BAUD_RATE = 9600  # Baud rate is irrelevant for USB communication according to WF API, but required by pyserial

def send_command(ser, command):
    ser.write(command.encode())
    time.sleep(0.1)  # Give the device some time to respond

def read_response(ser):
    response = ser.read_all().decode()
    return response

def main():
    # Open the COM port
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    
    try:
        # Example: Set frequency to 1000 MHz
        send_command(ser, 'f10.0')
        print("Frequency set to 10 MHz")
        
        # Example: Query current frequency
        send_command(ser, 'f?')
        response = read_response(ser)
        print(f"Current frequency: {response}")

        # Example: Set frequency to 1000 MHz
        send_command(ser, 'f50.0')
        print("Frequency set to 1000 MHz")

        # Example: Query current frequency
        send_command(ser, 'f?')
        response = read_response(ser)
        print(f"Current frequency: {response}")

        # Example: Query current power
        send_command(ser, 'W?')
        response = read_response(ser)
        print(f"Current power: {response}")

        # Example: Set power to 1 dBm
        send_command(ser, 'W1.0')
        print("Power set to 1 dBm")
        
        # Example: Query current power
        send_command(ser, 'W?')
        response = read_response(ser)
        print(f"Current power: {response}")

        # Example: Run a frequency sweep from 1000 MHz to 1010 MHz in steps of 1 MHz
        send_command(ser, 'l50.0')  # Set lower frequency
        send_command(ser, 'u100.0')  # Set upper frequency
        send_command(ser, 's10.0')     # Set step size
        send_command(ser, 'g1')       # Start sweep
        print("Running frequency sweep from 1000 MHz to 1010 MHz")
        
        # Give some time for the sweep to complete
        time.sleep(2)

        send_command(ser, 'f?')
        response = read_response(ser)
        print(f"Current frequency: {response}")

        send_command(ser, 'f?')
        response = read_response(ser)
        print(f"Current frequency: {response}")

        send_command(ser, 'f?')
        response = read_response(ser)
        print(f"Current frequency: {response}")

        
        # Stop the sweep
        send_command(ser, 'g0')
        print("Sweep stopped")

        send_command(ser, 'f?')
        response = read_response(ser)
        print(f"Current frequency: {response}")
        
    finally:
        # Close the COM port
        ser.close()

if __name__ == '__main__':
    main()
