from blacs.device_base_class import DeviceTab, define_state
from qtutils.qt.QtWidgets import (QVBoxLayout, QGridLayout, QLabel, QLineEdit, 
                                  QPushButton, QGroupBox, QComboBox, QDoubleSpinBox, QTextEdit)
from qtutils.qt.QtCore import Qt
from user_devices.Rydberg.KoheronCTL200.labscript_devices import KoheronCTL200

class KoheronCTL200Tab(DeviceTab):
    def initialise_GUI(self):
        layout = self.get_tab_layout()

        device_info = self.settings['connection_table'].find_by_name(self.device_name)
        self.com_port = device_info.properties['com_port']

        #Create device instance
        self.device = KoheronCTL200(self.device_name, None, self.com_port)
        
        # Create main control group
        main_group = QGroupBox("Main Controls")
        main_layout = QGridLayout()
        
        # Laser current control
        self.current_spinbox = QDoubleSpinBox()
        self.current_spinbox.setRange(0, 1000)
        self.current_spinbox.setSuffix(" mA")
        self.current_spinbox.setDecimals(3)
        main_layout.addWidget(QLabel("Laser Current:"), 0, 0)
        main_layout.addWidget(self.current_spinbox, 0, 1)
        self.set_current_button = QPushButton("Set Current")
        self.set_current_button.clicked.connect(self.on_set_current)        
        main_layout.addWidget(self.set_current_button, 0, 2)

        # Temperature control
        self.temp_spinbox = QDoubleSpinBox()
        self.temp_spinbox.setRange(500, 200000)
        self.temp_spinbox.setSuffix(" Ω")
        self.temp_spinbox.setDecimals(3)
        main_layout.addWidget(QLabel("Temperature (Resistance):"), 1, 0)
        main_layout.addWidget(self.temp_spinbox, 1, 1)
        self.set_temp_button = QPushButton("Set Temperature")
        self.set_temp_button.clicked.connect(self.on_set_temperature)
        main_layout.addWidget(self.set_temp_button, 1, 2)

        # Laser output control
        self.output_combo = QComboBox()
        self.output_combo.addItems(["Disabled", "Enabled"])
        main_layout.addWidget(QLabel("Laser Output:"), 2, 0)
        main_layout.addWidget(self.output_combo, 2, 1)
        self.set_output_button = QPushButton("Set Output")
        self.set_output_button.clicked.connect(self.on_set_output)
        main_layout.addWidget(self.set_output_button, 2, 2)

        # Interlock control
        self.interlock_combo = QComboBox()
        self.interlock_combo.addItems(["Disabled", "Enabled"])
        main_layout.addWidget(QLabel("Interlock:"), 3, 0)
        main_layout.addWidget(self.interlock_combo, 3, 1)
        self.set_interlock_button = QPushButton("Set Interlock")
        self.set_interlock_button.clicked.connect(self.on_set_interlock)
        main_layout.addWidget(self.set_interlock_button, 3, 2)

        main_group.setLayout(main_layout)
        layout.addWidget(main_group)

        # Create PID control group
        pid_group = QGroupBox("PID Control")
        pid_layout = QGridLayout()

        self.p_gain_spinbox = QDoubleSpinBox()
        self.p_gain_spinbox.setRange(0, 0.1)
        self.p_gain_spinbox.setDecimals(6)
        pid_layout.addWidget(QLabel("P Gain:"), 0, 0)
        pid_layout.addWidget(self.p_gain_spinbox, 0, 1)

        self.i_gain_spinbox = QDoubleSpinBox()
        self.i_gain_spinbox.setRange(0, 0.1)
        self.i_gain_spinbox.setDecimals(6)
        pid_layout.addWidget(QLabel("I Gain:"), 1, 0)
        pid_layout.addWidget(self.i_gain_spinbox, 1, 1)

        self.d_gain_spinbox = QDoubleSpinBox()
        self.d_gain_spinbox.setRange(0, 0.1)
        self.d_gain_spinbox.setDecimals(6)
        pid_layout.addWidget(QLabel("D Gain:"), 2, 0)
        pid_layout.addWidget(self.d_gain_spinbox, 2, 1)

        self.set_pid_button = QPushButton("Set PID Gains")
        self.set_pid_button.clicked.connect(self.on_set_pid_gains)
        pid_layout.addWidget(self.set_pid_button, 3, 0, 1, 2)

        pid_group.setLayout(pid_layout)
        layout.addWidget(pid_group)

        # Current Limit Control :)
        self.current_limit_spinbox = QDoubleSpinBox()
        self.current_limit_spinbox.setRange(0, 1000)
        self.current_limit_spinbox.setSuffix(" mA")
        self.current_limit_spinbox.setDecimals(3)
        main_layout.addWidget(QLabel("Current Limit:"), 4, 0)  # Assuming the previous controls used rows 0-3
        main_layout.addWidget(self.current_limit_spinbox, 4, 1)
        self.set_current_limit_button = QPushButton("Set Current Limit")
        self.set_current_limit_button.clicked.connect(self.on_set_current_limit)
        main_layout.addWidget(self.set_current_limit_button, 4, 2)

        # Save settings button
        self.save_settings_button = QPushButton("Save Settings")
        self.save_settings_button.clicked.connect(self.on_save_settings)
        layout.addWidget(self.save_settings_button)

        # Status display
        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)
        self.status_display.setMaximumHeight(100)
        layout.addWidget(self.status_display)

    MODE_MANUAL = 1

    @define_state(MODE_MANUAL, queue_state_indefinitely=True, delete_stale_states=True)
    def on_set_current(self, *args):
        current = self.current_spinbox.value()
        self.device.set_laser_current(current)
        command = self.device.command_list[-1]
        results = yield(self.queue_work(self.primary_worker, 'send_commands', [command]))
        self.update_status(f"Status: Laser current set to {current} mA - Response: {results}")

    @define_state(MODE_MANUAL, queue_state_indefinitely=True, delete_stale_states=True)
    def on_set_temperature(self, *args):
        resistance = self.temp_spinbox.value()
        self.device.set_temperature(resistance)
        command = self.device.command_list[-1]
        results = yield(self.queue_work(self.primary_worker, 'send_commands', [command]))
        self.update_status(f"Status: Temperature set to {resistance} Ω - Response: {results}")

    @define_state(MODE_MANUAL, queue_state_indefinitely=True, delete_stale_states=True)
    def on_set_output(self, *args):
        state = self.output_combo.currentIndex() == 1
        self.device.enable_laser(state)
        command = self.device.command_list[-1]
        results = yield(self.queue_work(self.primary_worker, 'send_commands', [command]))
        self.update_status(f"Status: Laser output {'enabled' if state else 'disabled'} - Response: {results}")

    @define_state(MODE_MANUAL, queue_state_indefinitely=True, delete_stale_states=True)
    def on_set_interlock(self, *args):
        state = self.interlock_combo.currentIndex() == 1
        self.device.set_interlock(state)
        command = self.device.command_list[-1]
        results = yield(self.queue_work(self.primary_worker, 'send_commands', [command]))
        self.update_status(f"Status: Interlock {'enabled' if state else 'disabled'} - Response: {results}")

    @define_state(MODE_MANUAL, queue_state_indefinitely=True, delete_stale_states=True)
    def on_set_pid_gains(self, *args):
        p_gain = self.p_gain_spinbox.value()
        i_gain = self.i_gain_spinbox.value()
        d_gain = self.d_gain_spinbox.value()
        self.device.set_pid_gains(p_gain, i_gain, d_gain)
        commands = self.device.command_list[-3:]
        results = yield(self.queue_work(self.primary_worker, 'send_commands', commands))
        self.update_status(f"Status: PID gains set - Response: {results}")

    @define_state(MODE_MANUAL, queue_state_indefinitely=True, delete_stale_states=True)
    def on_save_settings(self, *args):
        self.device.save_settings()
        command = self.device.command_list[-1]
        results = yield(self.queue_work(self.primary_worker, 'send_commands', [command]))
        self.update_status(f"Status: Settings saved - Response: {results}")
    
    @define_state(MODE_MANUAL, queue_state_indefinitely=True, delete_stale_states=True)
    def on_set_current_limit(self, *args):
        limit = self.current_limit_spinbox.value()
        self.device.set_current_limit(limit)
        command = self.device.command_list[-1]
        results = yield(self.queue_work(self.primary_worker, 'send_commands', [command]))
        self.update_status(f"Status: Current limit set to {limit} mA - Response: {results}")


    def initialise_workers(self):
        worker_initialisation_kwargs = {'com_port': self.com_port}
        self.create_worker(
            'main_worker',
            'user_devices.Rydberg.KoheronCTL200.blacs_workers.KoheronCTL200Worker',
            worker_initialisation_kwargs,
        )
        self.primary_worker = 'main_worker'
    
    def update_status(self, message):
        self.status_display.append(message)
        self.status_display.ensureCursorVisible()
        print(f"BLACS KoheronCTL200 Status: {message}")

    def set_laser_current(self, current):
        """Set the laser current in mA."""
        command = f"ilaser {current}"
        self.command_list.append(command)

    def set_temperature(self, resistance):
        """Set the temperature setpoint via thermistor resistance in Ohms."""
        command = f"rtset {resistance}"
        self.command_list.append(command)

    def enable_laser(self, state):
        """Enable or disable the laser output."""
        value = 1 if state else 0
        command = f"lason {value}"
        self.command_list.append(command)

    def set_interlock(self, state):
        """Enable or disable the interlock functionality."""
        value = 1 if state else 0
        command = f"lckon {value}"
        self.command_list.append(command)

    def set_pid_gains(self, p_gain, i_gain, d_gain):
        """Set the PID gains for temperature control."""
        commands = [
            f"pgain {p_gain}",
            f"igain {i_gain}",
            f"dgain {d_gain}"
        ]
        self.command_list.extend(commands)

    def save_settings(self):
        """Save the current configuration to internal memory."""
        command = "save"
        self.command_list.append(command)

    def get_laser_current(self):
        """Get the current laser current."""
        command = "ilaser"
        self.command_list.append(command)

    def get_temperature(self):
        """Get the current temperature (thermistor resistance)."""
        command = "rtact"
        self.command_list.append(command)

    def get_tec_current(self):
        """Get the TEC current."""
        command = "itec"
        self.command_list.append(command)

    def get_photodiode_current(self):
        """Get the photodiode current."""
        command = "iphd"
        self.command_list.append(command)

    def get_status(self):
        """Get the device status."""
        command = "status"
        command = self.device.command_list[-1]
        #self.command_list.append(command)
        results = yield(self.queue_work(self.primary_worker, 'send_commands', command))
        self.update_status(f"Status: PID gains set - Response: {results}")

    def set_current_limit(self, limit):
        """Set the software current limit in mA."""
        command = f"ilmax {limit}"
        self.command_list.append(command)

    def set_temp_protection(self, state):
        """Enable or disable temperature protection."""
        value = 1 if state else 0
        command = f"tprot {value}"
        self.command_list.append(command)

    def set_temp_limits(self, min_resistance, max_resistance):
        """Set the temperature protection limits via thermistor resistance."""
        commands = [
            f"rtmin {min_resistance}",
            f"rtmax {max_resistance}"
        ]
        self.command_list.extend(commands)

    def set_tec_voltage_limits(self, min_voltage, max_voltage):
        """Set the TEC voltage limits."""
        commands = [
            f"vtmin {min_voltage}",
            f"vtmax {max_voltage}"
        ]
        self.command_list.extend(commands)

    def get_error(self):
        """Get the error code."""
        command = "err"
        self.command_list.append(command)

    def clear_error(self):
        """Clear the error code."""
        command = "errclr"
        self.command_list.append(command)
    
   