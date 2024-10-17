from blacs.device_base_class import DeviceTab, define_state
from qtutils.qt.QtWidgets import (QVBoxLayout, QGridLayout, QLabel, QLineEdit, 
                                  QPushButton, QGroupBox, QComboBox, QDoubleSpinBox, QTextEdit)
from qtutils.qt.QtCore import Qt
from user_devices.Rydberg.WindfreakSynthUSB3.labscript_devices import WindfreakSynthUSB3
from qtutils import inmain_decorator

class WindfreakSynthUSB3Tab(DeviceTab):
    def initialise_GUI(self):
        layout = self.get_tab_layout()

        device_info = self.settings['connection_table'].find_by_name(self.device_name)
        self.com_port = device_info.properties['com_port']

        #Create device instance
        self.device = WindfreakSynthUSB3(self.device_name, None, self.com_port)
        
        # Create main control group
        main_group = QGroupBox("Main Controls")
        main_layout = QGridLayout()

        # Frequency control
        self.freq_spinbox = QDoubleSpinBox()
        self.freq_spinbox.setRange(0, 6000)
        self.freq_spinbox.setSuffix(" MHz")
        self.freq_spinbox.setDecimals(8)
        main_layout.addWidget(QLabel("Frequency:"), 0, 0)
        main_layout.addWidget(self.freq_spinbox, 0, 1)
        self.set_freq_button = QPushButton("Set Frequency")
        self.set_freq_button.clicked.connect(self.on_set_frequency)        
        main_layout.addWidget(self.set_freq_button, 0, 2)

        # Power control
        self.power_spinbox = QDoubleSpinBox()
        self.power_spinbox.setRange(-60, 20)
        self.power_spinbox.setSuffix(" dBm")
        self.power_spinbox.setDecimals(3)
        main_layout.addWidget(QLabel("Power:"), 1, 0)
        main_layout.addWidget(self.power_spinbox, 1, 1)
        self.set_power_button = QPushButton("Set Power")
        self.set_power_button.clicked.connect(self.on_set_power)
        main_layout.addWidget(self.set_power_button, 1, 2)

        # Output control
        self.output_combo = QComboBox()
        self.output_combo.addItems(["Disabled", "Enabled"])
        main_layout.addWidget(QLabel("Output:"), 2, 0)
        main_layout.addWidget(self.output_combo, 2, 1)
        self.set_output_button = QPushButton("Set Output")
        self.set_output_button.clicked.connect(self.on_set_output)
        main_layout.addWidget(self.set_output_button, 2, 2)

        # Reference control
        self.ref_combo = QComboBox()
        self.ref_combo.addItems(["External", "Internal"])
        main_layout.addWidget(QLabel("Reference:"), 3, 0)
        main_layout.addWidget(self.ref_combo, 3, 1)
        self.set_ref_button = QPushButton("Set Reference")
        self.set_ref_button.clicked.connect(self.on_set_reference)
        main_layout.addWidget(self.set_ref_button, 3, 2)

        main_group.setLayout(main_layout)
        layout.addWidget(main_group)

        # Create sweep control group
        sweep_group = QGroupBox("Frequency Sweep")
        sweep_layout = QGridLayout()

        self.start_freq_spinbox = QDoubleSpinBox()
        self.start_freq_spinbox.setRange(0, 6000)
        self.start_freq_spinbox.setSuffix(" MHz")
        sweep_layout.addWidget(QLabel("Start Frequency:"), 0, 0)
        sweep_layout.addWidget(self.start_freq_spinbox, 0, 1)

        self.stop_freq_spinbox = QDoubleSpinBox()
        self.stop_freq_spinbox.setRange(0, 6000)
        self.stop_freq_spinbox.setSuffix(" MHz")
        sweep_layout.addWidget(QLabel("Stop Frequency:"), 1, 0)
        sweep_layout.addWidget(self.stop_freq_spinbox, 1, 1)

        self.step_size_spinbox = QDoubleSpinBox()
        self.step_size_spinbox.setRange(0, 100)
        self.step_size_spinbox.setSuffix(" MHz")
        sweep_layout.addWidget(QLabel("Step Size:"), 2, 0)
        sweep_layout.addWidget(self.step_size_spinbox, 2, 1)

        self.step_time_spinbox = QDoubleSpinBox()
        self.step_time_spinbox.setRange(0, 1000)
        self.step_time_spinbox.setSuffix(" ms")
        sweep_layout.addWidget(QLabel("Step Time:"), 3, 0)
        sweep_layout.addWidget(self.step_time_spinbox, 3, 1)

        self.set_sweep_button = QPushButton("Set Sweep")
        self.set_sweep_button.clicked.connect(self.on_set_sweep)
        sweep_layout.addWidget(self.set_sweep_button, 4, 0, 1, 2)

        self.run_sweep_button = QPushButton("Run Single Sweep")
        self.run_sweep_button.clicked.connect(lambda: self.on_run_sweep(False))
        sweep_layout.addWidget(self.run_sweep_button, 5, 0)

        self.run_cont_sweep_button = QPushButton("Run Continuous Sweep")
        self.run_cont_sweep_button.clicked.connect(lambda: self.on_run_sweep(True))
        sweep_layout.addWidget(self.run_cont_sweep_button, 5, 1)

        self.stop_sweep_button = QPushButton("Stop Sweep")
        self.stop_sweep_button.clicked.connect(self.on_stop_sweep)
        sweep_layout.addWidget(self.stop_sweep_button, 6, 0, 1, 2)

        sweep_group.setLayout(sweep_layout)
        layout.addWidget(sweep_group)

        # Create modulation control group
        mod_group = QGroupBox("Modulation")
        mod_layout = QGridLayout()

        self.am_freq_spinbox = QDoubleSpinBox()
        self.am_freq_spinbox.setRange(0, 1000)
        self.am_freq_spinbox.setSuffix(" Hz")
        mod_layout.addWidget(QLabel("AM Frequency:"), 0, 0)
        mod_layout.addWidget(self.am_freq_spinbox, 0, 1)

        self.am_ontime_spinbox = QDoubleSpinBox()
        self.am_ontime_spinbox.setRange(0, 100)
        self.am_ontime_spinbox.setSuffix(" %")
        mod_layout.addWidget(QLabel("AM On-Time:"), 1, 0)
        mod_layout.addWidget(self.am_ontime_spinbox, 1, 1)

        self.set_am_button = QPushButton("Set AM Modulation")
        self.set_am_button.clicked.connect(self.on_set_am_modulation)
        mod_layout.addWidget(self.set_am_button, 2, 0, 1, 2)

        self.fm_freq_spinbox = QDoubleSpinBox()
        self.fm_freq_spinbox.setRange(0, 1000)
        self.fm_freq_spinbox.setSuffix(" Hz")
        mod_layout.addWidget(QLabel("FM Frequency:"), 3, 0)
        mod_layout.addWidget(self.fm_freq_spinbox, 3, 1)

        self.fm_dev_spinbox = QDoubleSpinBox()
        self.fm_dev_spinbox.setRange(0, 1000)
        self.fm_dev_spinbox.setSuffix(" kHz")
        mod_layout.addWidget(QLabel("FM Deviation:"), 4, 0)
        mod_layout.addWidget(self.fm_dev_spinbox, 4, 1)

        self.set_fm_button = QPushButton("Set FM Modulation")
        self.set_fm_button.clicked.connect(self.on_set_fm_modulation)
        mod_layout.addWidget(self.set_fm_button, 5, 0, 1, 2)

        mod_group.setLayout(mod_layout)
        layout.addWidget(mod_group)

        # Save settings button
        self.save_settings_button = QPushButton("Save Settings to EEPROM")
        self.save_settings_button.clicked.connect(self.on_save_settings)
        layout.addWidget(self.save_settings_button)

        # Status display
        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)
        self.status_display.setMaximumHeight(100)  # Adjust as needed
        layout.addWidget(self.status_display)

    MODE_MANUAL = 1

    @inmain_decorator()
    def get_spinbox_value(self, spinbox):
        return spinbox.value()

    @inmain_decorator()
    def get_combobox_index(self, combobox):
        return combobox.currentIndex()

    @define_state(MODE_MANUAL, queue_state_indefinitely=True, delete_stale_states=True)
    def on_set_frequency(self, *args):
        freq = self.get_spinbox_value(self.freq_spinbox)
        self.device.set_frequency(freq)
        command = self.device.command_list[-1]
        results = yield(self.queue_work(self.primary_worker, 'send_commands', [command]))
        self.update_status(f"Status: Frequency set to {freq} MHz - Response: {results}")

    @define_state(MODE_MANUAL, queue_state_indefinitely=True, delete_stale_states=True)
    def on_set_power(self, *args):
        power = self.get_spinbox_value(self.power_spinbox)
        self.device.set_power(power)
        command = self.device.command_list[-1]
        results = yield(self.queue_work(self.primary_worker, 'send_commands', [command]))
        self.update_status(f"Status: Power set to {power} dBm - Response: {results}")

    @define_state(MODE_MANUAL, queue_state_indefinitely=True, delete_stale_states=True)
    def on_set_output(self, *args):
        state = self.get_combobox_index(self.output_combo) == 1
        self.device.enable_output(state)
        command = self.device.command_list[-1]
        results = yield(self.queue_work(self.primary_worker, 'send_commands', [command]))
        self.update_status(f"Status: Output {'enabled' if state else 'disabled'} - Response: {results}")

    @define_state(MODE_MANUAL, queue_state_indefinitely=True, delete_stale_states=True)
    def on_set_reference(self, *args):
        index = self.get_combobox_index(self.ref_combo)
        source = 'internal' if index == 1 else 'external'
        self.device.set_reference(source)
        command = self.device.command_list[-1]
        results = yield(self.queue_work(self.primary_worker, 'send_commands', [command]))
        self.update_status(f"Status: Reference set to {source} - Response: {results}")

    @define_state(MODE_MANUAL, queue_state_indefinitely=True, delete_stale_states=True)
    def on_set_sweep(self, *args):
        start = self.get_spinbox_value(self.start_freq_spinbox)
        stop = self.get_spinbox_value(self.stop_freq_spinbox)
        step = self.get_spinbox_value(self.step_size_spinbox)
        time = self.get_spinbox_value(self.step_time_spinbox) / 1000  # Convert ms to s
        
        self.device.set_sweep(start, stop, step, time)
        commands = self.device.command_list[-4:]  # Assuming set_sweep adds 4 commands
        results = yield(self.queue_work(self.primary_worker, 'send_commands', commands))
        self.update_status(f"Status: Sweep parameters set - Response: {results}")
        self.device.command_list.clear()  # Clear the command list after execution

    @define_state(MODE_MANUAL, queue_state_indefinitely=True, delete_stale_states=True)
    def on_run_sweep(self, continuous, *args):
        self.device.run_sweep(continuous)
        command = self.device.command_list[-1]
        results = yield(self.queue_work(self.primary_worker, 'send_commands', [command]))
        sweep_type = "Continuous" if continuous else "Single"
        self.update_status(f"Status: {sweep_type} sweep started - Response: {results}")

    @define_state(MODE_MANUAL, queue_state_indefinitely=True, delete_stale_states=True)
    def on_stop_sweep(self, *args):
        self.device.stop_sweep()
        command = self.device.command_list[-1]
        results = yield(self.queue_work(self.primary_worker, 'send_commands', [command]))
        self.update_status(f"Status: Sweep stopped - Response: {results}")

    @define_state(MODE_MANUAL, queue_state_indefinitely=True, delete_stale_states=True)
    def on_set_am_modulation(self, *args):
        freq = yield(self.get_spinbox_value(self.am_freq_spinbox))
        on_time = yield(self.get_spinbox_value(self.am_ontime_spinbox)) / 100  # Convert percentage to ratio
        self.device.set_am_modulation(freq, on_time)
        commands = self.device.command_list[-2:]  # Assuming set_am_modulation adds 2 commands
        results = yield(self.queue_work(self.primary_worker, 'send_commands', commands))
        self.update_status(f"Status: AM modulation set - Response: {results}")

    @define_state(MODE_MANUAL, queue_state_indefinitely=True, delete_stale_states=True)
    def on_set_fm_modulation(self, *args):
        freq = yield(self.get_spinbox_value(self.fm_freq_spinbox))
        deviation = yield(self.get_spinbox_value(self.fm_dev_spinbox))
        self.device.set_fm_modulation(freq, deviation)
        commands = self.device.command_list[-2:]  # Assuming set_fm_modulation adds 2 commands
        results = yield(self.queue_work(self.primary_worker, 'send_commands', commands))
        self.update_status(f"Status: FM modulation set - Response: {results}")

    @define_state(MODE_MANUAL, queue_state_indefinitely=True, delete_stale_states=True)
    def on_save_settings(self, *args):
        self.device.save_settings()
        command = self.device.command_list[-1]
        results = yield(self.queue_work(self.primary_worker, 'send_commands', [command]))
        self.update_status(f"Status: Settings saved to EEPROM - Response: {results}")
        self.device.command_list.clear()  # Clear the command list after execution

    @inmain_decorator()
    def update_status(self, message):
        self.status_display.append(message)
        self.status_display.ensureCursorVisible()
        print(f"BLACS WindfreakSynthUSB3 Status: {message}")  # This will show in the BLACS terminal

    def initialise_workers(self):
        worker_initialisation_kwargs = {'com_port': self.com_port}
        self.create_worker(
            'main_worker',
            'user_devices.Rydberg.WindfreakSynthUSB3.blacs_workers.WindfreakSynthUSB3Worker',
            worker_initialisation_kwargs,
        )
        self.primary_worker = 'main_worker'