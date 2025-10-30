
# Lenia_Ammonia: Lenia with a Dynamic Physical Environment

This is a modification of Bert Chan's Lenia (using `Lenia_Ammonia.py`) that moves beyond simple mathematical rules and places Lenia organisms into a **simulated physical environment**.

The standard Lenia simulation is "disembodied"—organisms' rules don't depend on a physical world. This modification simulates a **liquid ammonia (NH₃) environment**, complete with thermodynamics, chemistry, and fluid dynamics.

The most important feature is a new **agent-environment feedback loop**:
1.  Organisms' metabolism generates **heat**.
2.  This heat creates **temperature gradients** in the liquid ammonia.
3.  These gradients cause **thermal convection currents**.
4.  The convection currents **physically move the organisms** through the world.

This allows organisms to **evolve propulsion** by weaponizing physics. Asymmetric shapes create asymmetric thrust, allowing them to "swim" by creating their own currents.



##  Demos

 Coming Soon!

##  Key Features

* **Ammonia Environment:** Simulation parameters are tuned for a liquid ammonia environment, featuring lower temperature, faster time scaling (`AMMONIA_T = 18`), and wider diffusion kernels (`AMMONIA_RING`) to simulate lower viscosity.
* **Thermal Dynamics:** Organisms generate metabolic heat (`HEAT_GENERATION`). This heat diffuses (`THERMAL_DIFFUSION`) and radiates to a configurable ambient temperature (`AMBIENT_TEMP`).
* **Convection Propulsion:** A new `apply_convection` function calculates temperature gradients (`np.gradient(self.temperature)`) and applies a physical shift (`scipy.ndimage.shift`) to the organisms, nutrients, and waste fields.
* **Metabolic Cycle:** Organisms consume `self.nutrients` (using Monod kinetics) and produce toxic `self.waste`, which inhibits growth. This creates local ecological pressures.
* **Environmental Features:** The world can be initialized with "hydrothermal" vents (`nutrient_sources`) and "ice patches" (`cold_zones`) to create a more complex landscape.

##  Requirements

This script requires several Python libraries. You can install them using `pip`:
```bash
pip install numpy scipy scikit-image pillow
pip install pyopencl reikna  # For GPU acceleration (optional but recommended)


## How to Run
Make sure all required libraries are installed.

Run the script from your terminal: python3 Lenia_Ammonia.py

 ## Key,Action
C+E,Toggle NH₃/H₂O Environment: Switches between the new ammonia physics and classic Lenia (water) parameters.
Shift+C+E,Toggle Temperature Dynamics: Turns the entire heat and convection simulation on or off.
Shift+C+N,Toggle Nutrient Dynamics: Turns nutrient consumption and regeneration on or off.
Shift+C+W,Toggle Waste Dynamics: Turns waste production and toxicity on or off.
Tab (6th view): Switches to a visualization mode (self.show_what==5) that displays nutrient (green) and waste (purple) concentrations.
  
  Everything is enabled by default except the nh3 environment 


 ## HAVE FUN !! =) 


