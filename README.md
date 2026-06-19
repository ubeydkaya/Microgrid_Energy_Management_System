# Microgrid Energy Management System

A desktop application that simulates a small renewable-energy **microgrid** and decides, in
real time, how to balance generation against load using a battery and a grid connection.

The app combines **solar** and **wind** generation, stores surplus in a **battery**, and
falls back to the **main grid** (import/export) when needed. Results are shown on a live
dashboard and can be saved to a history file for later review.

> Built with Python and PyQt5. Author: **Ubeydullah Kaya**.

---

## Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
  - [Physics & Formulas](#physics--formulas)
  - [Energy-Balance Logic](#energy-balance-logic)
  - [Cost Model](#cost-model)
- [Architecture](#architecture)
  - [Object-Oriented Design](#object-oriented-design)
  - [Class Overview](#class-overview)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Using the GUI](#using-the-gui)
  - [Operating Modes](#operating-modes)
- [Simulation History File](#simulation-history-file)
- [Testing](#testing)

---

## Features

- **Two renewable sources** — solar panel and wind turbine, each modelled with real physics.
- **Battery storage** — charges from surplus, discharges to cover deficits, and enforces
  configurable minimum/maximum state-of-charge (SOC) limits.
- **Grid connection** — automatically imports when generation is short and exports surplus,
  with a simple buy/sell cost model.
- **Live dashboard** — coloured ON/OFF/Import/Export indicators, an SOC progress bar, and a
  critical-battery warning.
- **Operating-mode presets** — Day, Night, Summer, and Winter scenarios fill the inputs with
  one click.
- **Persistent history** — save each run to a fixed-width text file and reload it (or any
  other results file) into a table.
- **Input validation** — invalid values raise clear errors that the GUI turns into friendly
  warnings instead of crashing.
- **Backend test suite** — console tests verify the formulas and balancing decisions.

---

## How It Works

Each simulation is a single **time step**: the controller reads the current inputs, computes
how much power each source produces, compares it with the load, and decides what the battery
and grid should do.

### Physics & Formulas

**Solar panel** (output in kW):

```
P_solar = (G × A × η) / 1000
```

- `G` — solar irradiance (W/m²)
- `A` — panel area (m²)
- `η` — efficiency (0–1)

**Wind turbine** (output in kW):

```
P_wind = (0.5 × ρ × A × v³ × η) / 1000
```

- `ρ` — air density, fixed at **1.225 kg/m³**
- `A` — rotor swept area (m²)
- `v` — wind speed (m/s)
- `η` — efficiency (0–1)

Both formulas divide by 1000 to convert watts to kilowatts.

### Energy-Balance Logic

The controller computes:

```
balance = total_generation − load_demand
```

and then acts on the sign of the balance (a tiny `EPSILON = 1e-6` tolerance treats
near-zero values as balanced, avoiding floating-point noise):

| Situation | Condition | Action |
|-----------|-----------|--------|
| **Surplus** | `balance > 0` | Charge the battery first; **export** whatever the battery can't absorb. |
| **Deficit** | `balance < 0` | Discharge the battery first; **import** whatever the battery can't supply. |
| **Balanced** | `balance ≈ 0` | Battery and grid stay **idle**. |

The battery never charges past its **max SOC** or discharges below its **min SOC**, so any
remaining surplus/deficit is handled by the grid.

### Cost Model

The grid uses fixed prices (per kWh):

| Action | Price | Effect on cost |
|--------|-------|----------------|
| Import (`BUY_PRICE`) | 0.20 | Positive cost (money spent) |
| Export (`SELL_PRICE`) | 0.10 | Negative cost (money earned) |

So `cost > 0` means the step cost money, and `cost < 0` means the step earned money.

---

## Architecture

The project follows a clean separation between **backend logic** and the **GUI**. The GUI
(`main_window.py`) only reads inputs, calls the backend, and displays results — all
calculations live in plain Python classes that can be tested without Qt.

### Object-Oriented Design

The codebase deliberately demonstrates the four core OOP principles:

- **Encapsulation** — every class keeps its data in private attributes (`_name`, `_soc`, …)
  exposed through getter/setter methods with validation.
- **Inheritance** — `SolarPanel` and `WindTurbine` extend the abstract `EnergySource`.
- **Polymorphism** — both subclasses override `calculate_power()`; the controller calls it
  without knowing the concrete type.
- **Abstraction** — `EnergySource.calculate_power()` raises `NotImplementedError`, forcing
  subclasses to provide their own implementation.

### Class Overview

| Class | File | Responsibility |
|-------|------|----------------|
| `EnergySource` | `energy_source.py` | Abstract base for all renewable sources. |
| `SolarPanel` | `energy_source.py` | Computes solar power from irradiance, area, efficiency. |
| `WindTurbine` | `energy_source.py` | Computes wind power from wind speed, swept area, efficiency. |
| `Battery` | `battery.py` | Stores energy; enforces SOC limits; charge/discharge logic. |
| `Load` | `components.py` | Holds the electrical demand. |
| `GridConnection` | `components.py` | Imports/exports energy and computes cost. |
| `MicrogridController` | `controller.py` | Orchestrates one simulation step and balances the system. |
| `SimulationResult` | `simulation_result.py` | Immutable data holder + text/table serialization. |
| `FileManager` | `file_manager.py` | Saves/loads results as a fixed-width history file. |
| `MainWindow` | `main_window.py` | The PyQt5 GUI; connects widgets to the backend. |

---

## Project Structure

```
Microgrid_Energy_Management_System/
├── main.py                  # Entry point — creates the window, starts the event loop
├── main_window.py           # GUI class (MainWindow): inputs, dashboard, history
├── microgrid.ui             # Qt Designer layout, loaded at runtime
│
├── energy_source.py         # EnergySource (abstract), SolarPanel, WindTurbine
├── battery.py               # Battery (storage + SOC limits)
├── components.py            # Load, GridConnection
├── controller.py            # MicrogridController (energy-balance logic)
├── simulation_result.py     # SimulationResult (data + serialization)
├── file_manager.py          # FileManager (save/load history)
│
├── test_backend.py          # Console tests for the backend logic
└── files/
    └── microgrid_uml.drawio # UML class diagram (draw.io)
```

> A `simulation_history.txt` file is created automatically next to the code the first time
> you save a result.

---

## Requirements

- **Python 3.8+**
- **PyQt5**

The backend (everything except `main_window.py` / `main.py`) uses only the Python standard
library — PyQt5 is required only for the GUI.

## Installation

```bash
pip install PyQt5
```

> Tip: use a virtual environment to keep dependencies isolated.
>
> ```bash
> python -m venv venv
> venv\Scripts\activate      # Windows
> source venv/bin/activate     # macOS / Linux
> pip install PyQt5
> ```

## Running the Application

From the project folder:

```bash
python main.py
```

The main window opens with default values already filled in, and any previously saved
history is loaded into the table automatically.

---

## Using the GUI

The window is split into three panels plus a history table:

1. **Input Parameters** — set solar irradiance/area/efficiency, wind speed/area/efficiency,
   load demand, and battery capacity/SOC/limits. An **Operating mode** dropdown applies
   presets.
2. **Microgrid Status** — live dashboard: Solar/Wind/Battery/Grid/Load indicators, the SOC
   progress bar, and a critical-battery warning.
3. **Results** — exact numbers for solar/wind/total generation, load, balance, SOC, battery
   and grid actions, grid amount, cost, and a one-line system status.

Buttons:

- **Run Simulation** — compute and display one step using the current inputs.
- **Save Result** — append the last result to the history file.
- **Clear** — reset the results panel and dashboard.
- **Refresh** — reload the default history file into the table.
- **Load File…** — open and display any saved results `.txt` file.

### Operating Modes

Selecting a mode fills the inputs with a preset scenario:

| Mode | Irradiance | Solar eff. | Wind speed | Wind eff. | Load |
|------|-----------|------------|-----------|-----------|------|
| Day | 900 W/m² | 18% | 7 m/s | 40% | 5 kW |
| Night | 0 W/m² | 18% | 9 m/s | 40% | 4 kW |
| Summer | 1000 W/m² | 18% | 5 m/s | 40% | 6 kW |
| Winter | 400 W/m² | 16% | 12 m/s | 40% | 8 kW |

Choosing **Normal** keeps whatever values you entered manually.

---

## Simulation History File

Results are stored as a human-readable, **fixed-width** text file so it reads like a table.
The first line is a header; each subsequent line is one simulation. Columns:

```
Timestamp  Solar(kW)  Wind(kW)  Total(kW)  Load(kW)  Balance(kW)  SOC(%)  Battery  Grid  GridAmt(kWh)  Cost  Status
```

`FileManager` writes the header automatically when the file is first created, and
`SimulationResult.from_text_row()` safely skips any malformed lines when reading.

---

## Testing

The backend logic can be verified without launching the GUI:

```bash
python test_backend.py
```

The suite checks:

- **Formulas** — solar and wind power match expected values.
- **Surplus** — battery charges, grid stays idle.
- **Surplus with export** — full battery, leftover energy is exported (negative cost).
- **Deficit** — battery discharges to its minimum, grid imports the rest (positive cost).
- **Balanced** — generation equals load, everything idle.
- **Validation** — invalid inputs raise `ValueError`.

A successful run prints `All backend tests passed.`
