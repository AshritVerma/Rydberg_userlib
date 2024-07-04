from labscript import start, stop
from labscriptlib.Rydberg.office_connection_table import cxn_table

if __name__ == '__main__':
    # Import and define the global variables for devices
    cxn_table()

    t = 0
    start()

    # Get status (this will be executed by the BLACS worker)
    ctl200.get_status()
    t += 1


    stop(t)