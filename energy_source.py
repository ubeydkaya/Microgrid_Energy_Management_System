# energy_source.py 
# defines EnergySource (base class), SolarPanel, and WindTurbine (subclasses).


class EnergySource:
    # Superclass: shared data/behaviour of every renewable source.

    def __init__(self, name, efficiency):
        self._name = name              # Source name
        self._efficiency = efficiency  # Efficiency as a decimal value (0.0 - 1.0)

    # Getter methods

    def get_name(self):
        return self._name

    def get_efficiency(self):
        return self._efficiency

    # Setter method (with validation)

    def set_efficiency(self, efficiency):
        # Efficiency must be a decimal between 0 and 1 (0% - 100%)
        if efficiency < 0 or efficiency > 1:
            raise ValueError("Efficiency must be between 0 and 1 (0% - 100%).")
        self._efficiency = efficiency

    # Polymorphic method used; every subclass provides its own implementation.

    def calculate_power(self):
        # The base class has no real source, so subclasses must override this.
        raise NotImplementedError("Subclasses must implement calculate_power().")

    def is_active(self):
        # A source is active when it currently produces power.
        return self.calculate_power() > 0

    def __str__(self):
        return f"{self._name}: {self.calculate_power():.3f} kW"


class SolarPanel(EnergySource):
    # A SolarPanel is an EnergySource.
    # Power = G * A * efficiency / 1000   

    def __init__(self, irradiance, area, efficiency):
        # Set the common data through the superclass constructor 
        EnergySource.__init__(self, "Solar Panel", efficiency)
        self._irradiance = irradiance   # G, solar irradiance in W/m^2
        self._area = area               # A, solar panel area in m^2
        self._validate()

    def _validate(self):
        # Check that the values are physically meaningful
        if self._irradiance < 0:
            raise ValueError("Solar irradiance cannot be negative.")
        if self._area < 0:
            raise ValueError("Solar panel area cannot be negative.")
        if self._efficiency < 0 or self._efficiency > 1:
            raise ValueError("Solar efficiency must be between 0% and 100%.")

    # Getters for the type-specific properties

    def get_irradiance(self):
        return self._irradiance

    def get_area(self):
        return self._area

    def calculate_power(self):
        # G * A * efficiency, divided by 1000 to convert W to kW.
        return (self._irradiance * self._area * self._efficiency) / 1000


class WindTurbine(EnergySource):
    # A WindTurbine is an EnergySource.
    # Power = 0.5 * rho * A * v^3 * efficiency / 1000  

    AIR_DENSITY = 1.225   # rho, air density in kg/m^3 (class constant)

    def __init__(self, wind_speed, swept_area, efficiency):
        EnergySource.__init__(self, "Wind Turbine", efficiency)
        self._wind_speed = wind_speed   # v, wind speed in m/s
        self._swept_area = swept_area   # A, rotor swept area in m^2
        self._validate()

    def _validate(self):
        if self._wind_speed < 0:
            raise ValueError("Wind speed cannot be negative.")
        if self._swept_area < 0:
            raise ValueError("Rotor swept area cannot be negative.")
        if self._efficiency < 0 or self._efficiency > 1:
            raise ValueError("Wind efficiency must be between 0% and 100%.")

    # Getters for the type-specific properties

    def get_wind_speed(self):
        return self._wind_speed

    def get_swept_area(self):
        return self._swept_area

    def calculate_power(self):
        # 0.5 * rho * A * v^3 * efficiency, divided by 1000 to convert W to kW.
        return (0.5 * self.AIR_DENSITY * self._swept_area *
                (self._wind_speed ** 3) * self._efficiency) / 1000
