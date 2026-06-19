# components.py 
# defines Load (electrical demand) and GridConnection (main grid interface).

class Load:
    # The electrical load of the microgrid.

    def __init__(self, demand):
        self._demand = demand   # Load demand in kW
        if self._demand < 0:
            raise ValueError("Load demand cannot be negative.")

    def get_demand(self):
        return self._demand

    def set_demand(self, demand):
        if demand < 0:
            raise ValueError("Load demand cannot be negative.")
        self._demand = demand

    def __str__(self):
        return f"Load: {self._demand:.3f} kW"


class GridConnection:
    # Connection to the main grid. Can import, export, or stay idle.
    
    # Fixed Price
    BUY_PRICE = 0.20    # cost of importing 1 kWh from the grid
    SELL_PRICE = 0.10   # income from exporting 1 kWh to the grid

    def __init__(self):
        self._action = "Idle"   # "Import" / "Export" / "Idle"
        self._amount = 0.0      # Energy imported or exported in kWh

    # Getter methods

    def get_action(self):
        return self._action

    def get_amount(self):
        return self._amount

    # Actions

    def import_energy(self, amount):
        # Energy taken from the grid to cover a deficit.
        self._action = "Import"
        self._amount = amount

    def export_energy(self, amount):
        # Surplus energy sent to the grid.
        self._action = "Export"
        self._amount = amount

    def set_idle(self):
        # Reset before a new simulation step.
        self._action = "Idle"
        self._amount = 0.0

    def get_cost(self):
        # Positive value = money spent (import).
        # Negative value = money earned (export).
        if self._action == "Import":
            return self._amount * self.BUY_PRICE
        elif self._action == "Export":
            return -self._amount * self.SELL_PRICE
        return 0.0

    def __str__(self):
        return f"Grid: {self._action} {self._amount:.3f} kWh"
