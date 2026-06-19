# battery.py
# defines Battery, which stores energy and enforces minimum and maximum SOC limits.


class Battery:
    # Stores energy for the microgrid.

    def __init__(self, capacity, soc, min_soc=20, max_soc=100):
        self._capacity = capacity   # Battery capacity in kWh
        self._soc = soc             # State of charge in percent (0 - 100)
        self._min_soc = min_soc     # Lowest allowed SOC in percent
        self._max_soc = max_soc     # Highest allowed SOC in percent
        self._action = "Idle"       # "Charging" / "Discharging" / "Idle"
        self._validate()

    def _validate(self):
        if self._capacity < 0:
            raise ValueError("Battery capacity cannot be negative.")
        if self._soc < 0 or self._soc > 100:
            raise ValueError("Battery state of charge must be between 0 and 100.")
        if self._min_soc < 0 or self._max_soc > 100 or self._min_soc > self._max_soc:
            raise ValueError("Invalid SOC limits (need 0 <= min <= max <= 100).")

    # Getter methods

    def get_capacity(self):
        return self._capacity

    def get_soc(self):
        return self._soc

    def get_min_soc(self):
        return self._min_soc

    def get_max_soc(self):
        return self._max_soc

    def get_action(self):
        return self._action

    # Energy helper methods (all in kWh)

    def get_stored_energy(self):
        # Energy currently stored in the battery.
        return self._capacity * self._soc / 100

    def get_free_capacity(self):
        # Battery capacity remaining until maximum SOC.
        max_energy = self._capacity * self._max_soc / 100
        return max(0, max_energy - self.get_stored_energy())

    def get_min_energy(self):
        # Energy that must always stay in the battery.
        return self._capacity * self._min_soc / 100

    def get_usable_energy(self):
        # Energy available for use above the minimum SOC.
        return max(0, self.get_stored_energy() - self.get_min_energy())

    def is_critical(self):
        # True when the battery is at or below its minimum SOC.
        return self._soc <= self._min_soc

    # Actions - each returns the actual energy charged/discharged (kWh)

    def charge(self, energy):
        # Store as much of energy, then raise the SOC.
        accepted = min(energy, self.get_free_capacity())
        if accepted > 0 and self._capacity > 0:
            self._soc += accepted / self._capacity * 100
            self._action = "Charging"
        return accepted

    def discharge(self, energy):
        # Deliver as much of energy as available, then lower the SOC.
        delivered = min(energy, self.get_usable_energy())
        if delivered > 0 and self._capacity > 0:
            self._soc -= delivered / self._capacity * 100
            self._action = "Discharging"
        return delivered

    def set_idle(self):
        # Reset the action before a new simulation step.
        self._action = "Idle"

    def __str__(self):
        return (f"Battery: {self._soc:.1f}% "
                f"({self.get_stored_energy():.2f} kWh) - {self._action}")
