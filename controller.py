# controller.py 
# defines MicrogridController, which balances generation and load each simulation step.

from simulation_result import SimulationResult


class MicrogridController:

    # Values smaller than this (kW) are treated as balanced to avoid floating-point rounding errors.
    EPSILON = 1e-6

    def __init__(self, solar, wind, battery, load, grid):
        # The controller manages the other components.
        self._solar = solar
        self._wind = wind
        self._battery = battery
        self._load = load
        self._grid = grid

    def run_simulation(self):
        # Calculate the generation of each source.
        solar_power = self._solar.calculate_power()
        wind_power = self._wind.calculate_power()
        total_generation = solar_power + wind_power

        # Energy balance: positive = surplus, negative = deficit.
        load_demand = self._load.get_demand()
        balance = total_generation - load_demand

        # Reset the battery and grid actions for this step.
        self._battery.set_idle()
        self._grid.set_idle()

        if balance > self.EPSILON:
            # Surplus: charge the battery first, export leftover.
            charged = self._battery.charge(balance)
            surplus_left = balance - charged
            if surplus_left > self.EPSILON:
                self._grid.export_energy(surplus_left)

        elif balance < -self.EPSILON:
            # Deficit: discharge the battery first, import other is missing.
            deficit = -balance
            delivered = self._battery.discharge(deficit)
            shortage = deficit - delivered
            if shortage > self.EPSILON:
                self._grid.import_energy(shortage)

        # Otherwise the system is balanced; battery and grid stay idle.

        # Build status text.
        status = self._build_status(balance)

        # Package everything into a SimulationResult object.
        return SimulationResult(
            solar_power=solar_power,
            wind_power=wind_power,
            total_generation=total_generation,
            load_demand=load_demand,
            balance=balance,
            soc=self._battery.get_soc(),
            battery_action=self._battery.get_action(),
            grid_action=self._grid.get_action(),
            grid_amount=self._grid.get_amount(),
            cost=self._grid.get_cost(),
            status=status,
        )

    def _build_status(self, balance):
        # Summarise the overall system state in one sentence.
        if self._battery.is_critical():
            return "Critical: battery at minimum level"
        if balance > self.EPSILON:
            return "Surplus generation - charging / exporting"
        elif balance < -self.EPSILON:
            return "Deficit - discharging / importing"
        return "Balanced - generation equals load"
