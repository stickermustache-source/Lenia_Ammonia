#  Lenia Ammonia: Life in Alien Oceans

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)

> *What would artificial life look like in the ammonia oceans of alien moons like Titan?*

An extension of [Bert Chan's Lenia](https://github.com/Chakazul/Lenia) that simulates organisms within a **physically realistic liquid ammonia environment**. Watch as cellular automata navigate through temperature gradients, hunt for nutrients, and avoid toxic waste—all emerging from simple rules interacting with a dynamic world.

---

##  Demos
![Enregistrement d’écran, le 2025-10-30 à 16 06 09-2](https://github.com/user-attachments/assets/9be9a778-f318-4484-b375-c274c5a373f2)

![Lenia_Ammonia_Demo](https://github.com/user-attachments/assets/d598d11b-6069-4dbb-bbc5-43e2bc61e190)

**[ Watch Full Demo Video](https://youtu.be/wKBzmHFFQT4?si=AofKQiohAho3JYX9) 

---

##  What Makes This Different?

Standard Lenia is **"disembodied"**—organisms exist in abstract mathematical space. This project gives them a **physical world** to live in.

###  **Physical Environment**
- **Liquid ammonia ocean** (195K - 240K)
- Realistic thermodynamics (heat generation, diffusion, convection)
- Lower viscosity than water → faster, more fluid movements

###  **Chemical Ecology**
- **Nutrient depletion**: Organisms consume resources
- **Waste accumulation**: Metabolism produces toxins
- **Chemical signals**: Pheromone-like communication
- **Monod kinetics**: Realistic growth limitation

###  **Adaptive Behaviors** *(NEW!)*
- **REST**: High nutrients → grow and stay
- **HUNT**: Low nutrients → active foraging  
- **FLEE**: High toxicity → escape behavior
- **Emergent chemotaxis** without explicit programming

###  **Thermal Propulsion**
- Organisms generate metabolic heat
- Creates temperature gradients → convection currents
- Organisms get **physically transported** by fluid motion
- Asymmetric shapes create directional thrust → "swimming"!

---

##  Scientific Motivation

**Exobiology:** Saturn's moon Titan has vast liquid methane-ethane lakes. Jupiter's moons Europa and Enceladus may harbor subsurface ammonia oceans. What would life look like in these environments?

**Artificial Life:** Most CA models exist in abstract space. This project explores:
- Embodied cognition in cellular automata
- Environment-organism feedback loops
- Emergent adaptive behaviors from physical constraints

**Inspiration:** Combines ideas from:
- Lenia & Expanded Universe (Bert Chan)
- SmoothLife (Rafler, 2011)
- Active matter physics
- Bacterial chemotaxis

---

##  Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/stickermustache-source/Lenia_Ammonia.git
cd Lenia_Ammonia

# Install dependencies
pip install numpy scipy scikit-image pillow

# Optional: GPU acceleration (recommended!)
pip install pyopencl reikna
```

### Run the Simulation

```bash
# Standard version
python3 Lenia_Ammonia.py

# With adaptive behaviors (recommended!)
python3 Lenia_Ammonia_V2_comportements.py
```

---

## 🎮 Controls & Features

### Environment Toggle

 #EVERYTHING IS ENABLED BY DEFAULT
 
| Key | Action |
|-----|--------|
| `Ctrl+E` | Toggle NH₃/H₂O environment parameters |
| `Shift+Ctrl+E` | Toggle temperature dynamics |
| `Shift+Ctrl+N` | Toggle nutrient consumption |
| `Shift+Ctrl+W` | Toggle waste production |
| `Shift+Ctrl+S` | Toggle chemical signals |
| `Shift+Ctrl+B` | **Toggle adaptive behaviors** *(NEW!)* |

### Visualization Modes
| Key | View |
|-----|------|
| `Tab` | Cycle through views |
| View 0 | Organisms (standard) |
| View 1 | Growth potential field |
| View 2 | Growth field |
| View 3 | Interaction kernel |
| View 4 | Object detection map |
| View 5 | **Nutrients & Waste** (green/red/purple) |
| View 6 | **Behavioral States** (rest/hunt/flee) *(NEW!)* |

### Other Controls
- `Space` - Pause/Resume
- `R` - Random reset
- `C` - Clear world
- See original Lenia documentation for more

---

## 📊 Key Parameters

### Ammonia Environment
```python
AMMONIA_RING = {'r':0.75, 'w':0.6, 'b':1}  # Wider kernel (lower viscosity)
AMMONIA_M = 0.08        # Lower optimal growth (cold environment)
AMMONIA_S = 0.008       # Narrower growth window
AMMONIA_T = 18          # Faster time scaling (higher mobility)
AMMONIA_R = DEF_R * 1.5 # Larger interaction radius
```

### Physical Constants
```python
# Temperature
AMBIENT_TEMP = 208.0 K     # ~65K below water freezing
TEMP_RANGE = 195K - 240K   # Liquid ammonia range
THERMAL_DIFFUSION = 0.35   # Heat spreads quickly

# Ecology
NUTRIENT_REGEN = 0.004     # Slow replenishment
WASTE_DECAY = 0.008        # Biological breakdown
CONVECTION_STRENGTH = 0.008 # Fluid motion intensity
```

### Behavioral Thresholds
```python
REST:  nutrients > 0.7  → +20% growth
HUNT:  nutrients < 0.3  → -10% growth (encourage movement)
FLEE:  waste > 0.6      → -40% growth (escape pressure)
```

---

##  How It Works

### Agent-Environment Feedback Loop

```
┌─────────────────────────────────────────┐
│  Organisms consume nutrients            │
│         ↓                                │
│  Metabolism generates heat               │
│         ↓                                │
│  Heat creates temperature gradients     │
│         ↓                                │
│  Gradients drive convection currents    │
│         ↓                                │
│  Currents physically move organisms     │
│         ↓                                │
│  Organisms find new resources           │
└─────────────────────────────────────────┘
```

### Adaptive Behavior Emergence

Organisms don't "know" they're hunting or fleeing—behaviors emerge from local rules:

1. **Nutrient sensing** → Growth modulation
2. **Growth asymmetry** → Directional bias  
3. **Waste avoidance** → Migration pressure
4. **Result:** Chemotaxis without explicit pathfinding!

---

##  Project Structure

```
Lenia_Ammonia/
├── Lenia_Ammonia.py                      # Core simulation
├── Lenia_Ammonia_V2_comportements.py     # With adaptive behaviors
├── COMPORTEMENTS_ADAPTATIFS_README.md    # Behavior system docs
├── README.md                             # This file
└── demos/                                # (TODO) Videos and GIFs
```

---

##  Contributing

This is an open-source exploration! Contributions welcome:

-  Bug reports and fixes
-  New features (different environments, behaviors)
-  Data analysis tools
-  Visualization improvements
-  Documentation enhancements

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

##  About This Project

This project emerged from a creative exploration combining:
- **Original concept and direction** by the author
- **Implementation** developed through collaboration with Claude AI (Anthropic)
- **Goal:** Demonstrate what's possible in human-AI research partnerships

This is shared as **open-source proof-of-concept** to:
- Inspire the artificial life community
- Explore exobiological scenarios
- Advance cellular automata research
- Show new paradigms of human-AI collaboration

---

##  References & Inspiration

### Core Papers
- Chan, B. W.-C. (2019). *Lenia - Biology of Artificial Life.* Complex Systems, 28(3).
- Chan, B. W.-C. (2020). *Lenia and Expanded Universe.* ALIFE 2020 Proceedings.
- Rafler, S. (2011). *Generalization of Conway's "Game of Life" to a continuous domain - SmoothLife.*

### Exobiology Context
- Titan's hydrocarbon seas (Cassini mission)
- Europa & Enceladus subsurface oceans
- Ammonia as a potential biosolvent

### Related Projects
- [Original Lenia](https://github.com/Chakazul/Lenia) by Bert Chan
- [Lenia Extended Universe](https://chakazul.github.io/lenia.html)
- [SmoothLife](http://arxiv.org/abs/1111.1567)

---

##  License

MIT License - See [LICENSE.md](LICENSEmd) file for details.

**Attribution:** This project builds upon Bert Chan's Lenia. Please cite both:
- This project for the environmental extensions
- Bert Chan's original Lenia for the CA framework

---

##  Acknowledgments

- **Bert Chan** for creating Lenia and inspiring this work
- **Anthropic** for Claude AI development tools
- The **artificial life community** for decades of fascinating research
- **You** for being curious about life in alien oceans! 🚀

---

##  Contact & Discussion

- **GitHub Issues:** Bug reports and feature requests
- **Discussions:** Questions and ideas
- **Reddit:** r/alife, r/cellular_automata
- **Twitter:** Tag your demos with #LeniaAmmonia

---

<div align="center">

**⭐ Star this repo if you find it interesting!**


[🔬 Explore the Code](https://github.com/stickermustache-source/Lenia_Ammonia) • [🎮 Try It Yourself](https://github.com/stickermustache-source/Lenia_Ammonia#quick-start) • [🤝 Contribute](CONTRIBUTING.md)

</div>
