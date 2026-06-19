# test_backend.py 
# console tests for the calculation logic; run to verify formulas and energy-balance decisions.

from energy_source import SolarPanel, WindTurbine
from battery import Battery
from components import Load, GridConnection
from controller import MicrogridController


def almost_equal(a, b, tol=0.001):
    # True if two numbers are equal within a small tolerance.
    return abs(a - b) < tol


def test_formulas():
    solar = SolarPanel(1000, 1.6, 0.18)      # G=1000, A=1.6, eff=18%
    wind = WindTurbine(8, 10, 0.40)          # v=8, A=10, eff=40%
    assert almost_equal(solar.calculate_power(), 0.288), solar.calculate_power()
    assert almost_equal(wind.calculate_power(), 1.2544), wind.calculate_power()
    print("OK  formulas: solar=0.288 kW, wind=1.2544 kW")


def test_surplus():
    # Generation greater than load -> battery charges, no import.
    solar = SolarPanel(1000, 1.6, 0.18)      # 0.288 kW
    wind = WindTurbine(8, 10, 0.40)          # 1.2544 kW -> total 1.5424 kW
    battery = Battery(10, 50, 20, 100)       # 10 kWh, 50% SOC
    load = Load(1.0)
    grid = GridConnection()
    result = MicrogridController(solar, wind, battery, load, grid).run_simulation()
    assert result.get_battery_action() == "Charging", result.get_battery_action()
    assert result.get_grid_action() == "Idle", result.get_grid_action()
    assert result.get_soc() > 50.0, result.get_soc()
    print("OK  surplus: battery Charging, grid Idle, SOC rose to "
          f"{result.get_soc():.2f}%")


def test_surplus_with_export():
    # Big surplus, small battery room -> battery fills, rest is exported.
    solar = SolarPanel(1000, 5, 0.18)        # 0.9 kW
    wind = WindTurbine(12, 10, 0.40)         # ~4.2336 kW
    battery = Battery(2, 95, 20, 100)        # almost full, little room
    load = Load(0.5)
    grid = GridConnection()
    result = MicrogridController(solar, wind, battery, load, grid).run_simulation()
    assert result.get_grid_action() == "Export", result.get_grid_action()
    assert result.get_cost() < 0, result.get_cost()   # exporting earns money
    print("OK  export: grid Export "
          f"{result.get_grid_amount():.2f} kWh, cost={result.get_cost():.2f}")


def test_deficit():
    # Generation less than load -> battery discharges, grid imports the rest.
    solar = SolarPanel(0, 1.6, 0.18)         # 0 kW (night)
    wind = WindTurbine(0, 10, 0.40)          # 0 kW (no wind)
    battery = Battery(10, 50, 20, 100)       # 5 kWh stored, 3 kWh usable
    load = Load(5.0)
    grid = GridConnection()
    result = MicrogridController(solar, wind, battery, load, grid).run_simulation()
    assert result.get_battery_action() == "Discharging", result.get_battery_action()
    assert result.get_grid_action() == "Import", result.get_grid_action()
    assert almost_equal(result.get_soc(), 20.0), result.get_soc()     # down to min
    assert result.get_cost() > 0, result.get_cost()                  # importing costs money
    print("OK  deficit: battery Discharging to 20%, grid Import "
          f"{result.get_grid_amount():.2f} kWh, cost={result.get_cost():.2f}")


def test_balanced():
    # Generation equals load -> everything idle.
    solar = SolarPanel(1000, 1.6, 0.18)      # 0.288 kW
    wind = WindTurbine(8, 10, 0.40)          # 1.2544 kW -> total 1.5424 kW
    battery = Battery(10, 50, 20, 100)
    load = Load(1.5424)
    grid = GridConnection()
    result = MicrogridController(solar, wind, battery, load, grid).run_simulation()
    assert result.get_battery_action() == "Idle", result.get_battery_action()
    assert result.get_grid_action() == "Idle", result.get_grid_action()
    print("OK  balanced: battery Idle, grid Idle")


def test_validation():
    # Invalid inputs must raise ValueError (the GUI turns this into a warning).
    for bad in (lambda: SolarPanel(-1, 1, 0.1),
                lambda: Battery(10, 150, 20, 100),
                lambda: Battery(10, 50, 80, 20),
                lambda: Load(-5)):
        try:
            bad()
            assert False, "expected ValueError"
        except ValueError:
            pass
    print("OK  validation: invalid inputs raise ValueError")


if __name__ == "__main__":
    test_formulas()
    test_surplus()
    test_surplus_with_export()
    test_deficit()
    test_balanced()
    test_validation()
    print("\nAll backend tests passed.")
