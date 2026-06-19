# simulation_result.py 
# defines SimulationResult, which holds all data from one simulation run.

from datetime import datetime


class SimulationResult:

    # Each tuple defines a column as (header name, fixed char width); width 0 means the rest of the line.
    COLUMNS = [
        ("Timestamp",     22),
        ("Solar(kW)",     11),
        ("Wind(kW)",      11),
        ("Total(kW)",     11),
        ("Load(kW)",      11),
        ("Balance(kW)",   13),
        ("SOC(%)",         9),
        ("Battery",       13),
        ("Grid",          10),
        ("GridAmt(kWh)",  14),
        ("Cost",          11),
        ("Status",         0),
    ]

    def __init__(self, solar_power, wind_power, total_generation, load_demand,
                 balance, soc, battery_action, grid_action, grid_amount,
                 cost, status, timestamp=None):
        # If no timestamp is given, use the current date and time.
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._timestamp = timestamp
        self._solar_power = solar_power
        self._wind_power = wind_power
        self._total_generation = total_generation
        self._load_demand = load_demand
        self._balance = balance
        self._soc = soc
        self._battery_action = battery_action
        self._grid_action = grid_action
        self._grid_amount = grid_amount
        self._cost = cost
        self._status = status

    # Getter methods (used by the GUI to display the results)

    def get_timestamp(self):
        return self._timestamp

    def get_solar_power(self):
        return self._solar_power

    def get_wind_power(self):
        return self._wind_power

    def get_total_generation(self):
        return self._total_generation

    def get_load_demand(self):
        return self._load_demand

    def get_balance(self):
        return self._balance

    def get_soc(self):
        return self._soc

    def get_battery_action(self):
        return self._battery_action

    def get_grid_action(self):
        return self._grid_action

    def get_grid_amount(self):
        return self._grid_amount

    def get_cost(self):
        return self._cost

    def get_status(self):
        return self._status

    # Table / text-file conversion

    @classmethod
    def headers(cls):
        # The column header names (used for the history table and the txt file).
        return [header for header, width in cls.COLUMNS]

    def to_values(self):
        # The cell values in column order, as strings.
        # Used both for the history table and for the saved txt row.
        return [
            self._timestamp,
            f"{self._solar_power:.3f}",
            f"{self._wind_power:.3f}",
            f"{self._total_generation:.3f}",
            f"{self._load_demand:.3f}",
            f"{self._balance:.3f}",
            f"{self._soc:.1f}",
            self._battery_action,
            self._grid_action,
            f"{self._grid_amount:.3f}",
            f"{self._cost:.3f}",
            self._status,
        ]

    @classmethod
    def text_header(cls):
        # The header line of the txt file, padded to the column widths.
        return cls._pad_row([header for header, width in cls.COLUMNS])

    def to_text_row(self):
        # One result as a fixed-width line, so the file looks like a table.
        return self._pad_row(self.to_values())

    @classmethod
    def _pad_row(cls, values):
        # Pad each value to its column width.
        parts = []
        for (header, width), value in zip(cls.COLUMNS, values):
            parts.append(value if width == 0 else value.ljust(width))
        return "".join(parts).rstrip()

    @classmethod
    def from_text_row(cls, line):
        # Build a SimulationResult from one fixed-width line.
        # Returns None if the line is broken.
        line = line.rstrip("\n")
        if line.strip() == "":
            return None
        values = []
        pos = 0
        for header, width in cls.COLUMNS:
            if width == 0:
                values.append(line[pos:].strip())
            else:
                values.append(line[pos:pos + width].strip())
                pos += width
        try:
            return cls(
                timestamp=values[0],
                solar_power=float(values[1]),
                wind_power=float(values[2]),
                total_generation=float(values[3]),
                load_demand=float(values[4]),
                balance=float(values[5]),
                soc=float(values[6]),
                battery_action=values[7],
                grid_action=values[8],
                grid_amount=float(values[9]),
                cost=float(values[10]),
                status=values[11],
            )
        except (ValueError, IndexError):
            # A number column was not a valid number -> broken row.
            return None

    def __str__(self):
        return (f"[{self._timestamp}] "
                f"Gen: {self._total_generation:.2f} kW | "
                f"Load: {self._load_demand:.2f} kW | "
                f"Balance: {self._balance:.2f} kW | "
                f"Battery: {self._battery_action} | "
                f"Grid: {self._grid_action} | {self._status}")
