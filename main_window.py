# main_window.py 
# defines MainWindow, the only GUI class; connects the interface to the backend logic.

import os

from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QFileDialog

from energy_source import SolarPanel, WindTurbine
from battery import Battery
from components import Load, GridConnection
from controller import MicrogridController
from file_manager import FileManager
from simulation_result import SimulationResult

# Absolute path of this file's folder, used to find the .ui file and history file from any location.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UI_FILE = os.path.join(BASE_DIR, "microgrid.ui")
HISTORY_FILE = os.path.join(BASE_DIR, "simulation_history.txt")

# Preset input values for each operating mode.
# Each preset is: (irradiance, solar_eff, wind_speed, wind_eff, load_demand)
MODE_PRESETS = {
    "Day":    (900, 18, 7, 40, 5),
    "Night":  (0, 18, 9, 40, 4),
    "Summer": (1000, 18, 5, 40, 6),
    "Winter": (400, 16, 12, 40, 8),
}

# Colours used for the dashboard indicators.
GREY = "#bdc3c7"
GREEN = "#2ecc71"
ORANGE = "#e67e22"
RED = "#e74c3c"
BLUE = "#3498db"


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi(UI_FILE, self)               # load every widget onto self
        self.setWindowTitle("Microgrid Energy Management System by Ubeydullah Kaya")
        self._file_manager = FileManager(HISTORY_FILE)
        self._last_result = None                # last simulation, kept for saving
        self._connect_signals()
        self.on_refresh_history()               # show saved history at startup

    def _connect_signals(self):
        # Connect each widget's signal to the matching slot method.
        self.btnSimulate.clicked.connect(self.on_simulate)
        self.btnSave.clicked.connect(self.on_save)
        self.btnClear.clicked.connect(self.on_clear)
        # Keep the SOC slider and spin box in sync.
        self.sliderSOC.valueChanged.connect(self.spinSOC.setValue)
        self.spinSOC.valueChanged.connect(self.sliderSOC.setValue)
        # Operating-mode presets.
        self.comboMode.currentTextChanged.connect(self.on_mode_changed)
        self.btnRefreshHistory.clicked.connect(self.on_refresh_history)
        self.btnLoadFile.clicked.connect(self.on_load_file)

    # Event handlers

    def on_simulate(self):
        # Read the inputs, run the simulation, and show the results.
        try:
            solar = SolarPanel(self.dsbSolarIrradiance.value(),
                               self.dsbSolarArea.value(),
                               self.dsbSolarEff.value() / 100)
            wind = WindTurbine(self.dsbWindSpeed.value(),
                               self.dsbWindArea.value(),
                               self.dsbWindEff.value() / 100)
            battery = Battery(self.dsbBatteryCapacity.value(),
                              self.spinSOC.value(),
                              self.dsbMinSOC.value(),
                              self.dsbMaxSOC.value())
            load = Load(self.dsbLoadDemand.value())
            grid = GridConnection()

            controller = MicrogridController(solar, wind, battery, load, grid)
            result = controller.run_simulation()

            self._last_result = result
            self._show_results(result)
            self._update_dashboard(result)
            self.statusBar().showMessage("Simulation completed.", 3000)

        except ValueError as e:
            # Invalid user input (e.g. negative value, SOC out of range).
            QMessageBox.warning(self, "Invalid Input", str(e))
        except Exception as e:
            # Any other unexpected error - the program must not crash.
            QMessageBox.critical(self, "Unexpected Error", str(e))

    def on_save(self):
        # Save the last simulation result to the history file.
        if self._last_result is None:
            QMessageBox.information(self, "No Result",
                                    "Please run a simulation before saving.")
            return
        try:
            self._file_manager.save_result(self._last_result)
            self.on_refresh_history()
            self.statusBar().showMessage("Result saved to file.", 3000)
        except IOError as e:
            QMessageBox.critical(self, "File Error", str(e))

    def on_clear(self):
        # Reset the result labels and the dashboard.
        self._last_result = None
        for label in (self.lblSolarPower, self.lblWindPower, self.lblTotalGen,
                      self.lblLoadValue, self.lblBalance, self.lblSOCValue,
                      self.lblBatteryAction, self.lblGridAction,
                      self.lblGridAmount, self.lblSystemStatus, self.lblCost):
            label.setText("-")
        self.lblCriticalWarning.setText("")
        self.progressSOC.setValue(0)
        self._set_indicator(self.lblSolarStatus, "☀️ Solar: -", GREY)
        self._set_indicator(self.lblWindStatus, "💨 Wind: -", GREY)
        self._set_indicator(self.lblBatteryStatus, "🔋 Battery: -", GREY)
        self._set_indicator(self.lblGridStatus, "🔌 Grid: -", GREY)
        self._set_indicator(self.lblLoadStatus, "⚡ Load: -", GREY)

    def on_mode_changed(self, mode):
        # Load preset input values when an operating mode is chosen.
        if mode not in MODE_PRESETS:
            return   # Normal -> keep the user's own values
        irradiance, solar_eff, wind_speed, wind_eff, load = MODE_PRESETS[mode]
        self.dsbSolarIrradiance.setValue(irradiance)
        self.dsbSolarEff.setValue(solar_eff)
        self.dsbWindSpeed.setValue(wind_speed)
        self.dsbWindEff.setValue(wind_eff)
        self.dsbLoadDemand.setValue(load)

    def on_refresh_history(self):
        # Load the saved results from the default history file and show them.
        try:
            results = self._file_manager.load_results()
        except IOError as e:
            QMessageBox.critical(self, "File Error", str(e))
            return
        self._fill_history_table(results)

    def on_load_file(self):
        # Let the user pick a saved results file and show it in the table.
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Simulation Results", BASE_DIR,
            "Text files (*.txt);;All files (*)")
        if not path:
            return   
        try:
            results = self._file_manager.load_results(path)
        except IOError as e:
            QMessageBox.critical(self, "File Error", str(e))
            return
        if not results:
            QMessageBox.information(self, "No Results",
                                    "No readable results were found in this file.")
            return
        self._fill_history_table(results)
        self.statusBar().showMessage(f"Loaded {len(results)} result(s).", 3000)

    def _fill_history_table(self, results):
        # Show a list of SimulationResult objects in the history table.
        headers = SimulationResult.headers()
        self.tableHistory.setColumnCount(len(headers))
        self.tableHistory.setHorizontalHeaderLabels(headers)
        self.tableHistory.setRowCount(len(results))
        for row_index, result in enumerate(results):
            for col_index, cell in enumerate(result.to_values()):
                self.tableHistory.setItem(row_index, col_index,
                                          QTableWidgetItem(cell))

    # Helper methods 

    def _show_results(self, result):
        # Fill the result labels with the calculated values.
        self.lblSolarPower.setText(f"{result.get_solar_power():.3f} kW")
        self.lblWindPower.setText(f"{result.get_wind_power():.3f} kW")
        self.lblTotalGen.setText(f"{result.get_total_generation():.3f} kW")
        self.lblLoadValue.setText(f"{result.get_load_demand():.3f} kW")
        self.lblBalance.setText(f"{result.get_balance():.3f} kW")
        self.lblSOCValue.setText(f"{result.get_soc():.1f} %")
        self.lblBatteryAction.setText(result.get_battery_action())
        self.lblGridAction.setText(result.get_grid_action())
        self.lblGridAmount.setText(f"{result.get_grid_amount():.3f} kWh")
        self.lblCost.setText(f"{result.get_cost():.3f}")
        self.lblSystemStatus.setText(result.get_status())

    def _update_dashboard(self, result):
        # Update the visual dashboard: progress bar + coloured indicators.
        self.progressSOC.setValue(int(result.get_soc()))

        solar_on = result.get_solar_power() > 0
        wind_on = result.get_wind_power() > 0
        self._set_indicator(self.lblSolarStatus,
                            "☀️ Solar: ON" if solar_on else "☀️ Solar: OFF",
                            GREEN if solar_on else GREY)
        self._set_indicator(self.lblWindStatus,
                            "💨 Wind: ON" if wind_on else "💨 Wind: OFF",
                            GREEN if wind_on else GREY)

        battery_colours = {"Charging": GREEN, "Discharging": ORANGE, "Idle": GREY}
        self._set_indicator(self.lblBatteryStatus,
                            f"🔋 Battery: {result.get_battery_action()}",
                            battery_colours.get(result.get_battery_action(), GREY))

        grid_colours = {"Import": RED, "Export": BLUE, "Idle": GREY}
        self._set_indicator(self.lblGridStatus,
                            f"🔌 Grid: {result.get_grid_action()}",
                            grid_colours.get(result.get_grid_action(), GREY))

        # Load indicator
        load_supplied = result.get_balance() >= 0
        self._set_indicator(self.lblLoadStatus,
                            "⚡ Load: Supplied" if load_supplied else "⚡ Load: Deficit",
                            GREEN if load_supplied else RED)

        # Critical / warning message
        if "Critical" in result.get_status():
            self.lblCriticalWarning.setText("Battery at critical level!")
            self.lblCriticalWarning.setStyleSheet("color: #c0392b; font-weight: bold;")
        elif result.get_grid_action() == "Import":
            self.lblCriticalWarning.setText("Generation insufficient - importing from grid.")
            self.lblCriticalWarning.setStyleSheet("color: #e67e22; font-weight: bold;")
        else:
            self.lblCriticalWarning.setText("")

    def _set_indicator(self, label, text, colour):
        # Show 'text' on a coloured background (used for the ON/OFF indicators).
        label.setText(text)
        label.setStyleSheet(f"background-color: {colour}; color: white; "
                            f"padding: 4px; border-radius: 4px;")
