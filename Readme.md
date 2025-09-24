# 🛡️ AEGIS Drone Swarm Simulation

**AEGIS (Autonomous Engagement through Generalized Intelligent Swarming)** is a defense simulation project that demonstrates intelligent drone swarm coordination to counter hostile autonomous drones.  

This repository contains the full simulation code that you can run directly in **VS Code**.  

---

## 🚀 Quick Setup in VS Code

Follow these steps to run the project on your system:

### 1. Clone this repository
Open your VS Code terminal and run:
```bash
git clone https://github.com/Symphony007/SIH_Drone_Algo.git
cd SIH_Drone_Algo
```

### 2. Create a Virtual Environment
It's recommended to keep dependencies isolated.

**Windows (PowerShell):**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Make sure pip is updated, then install requirements:
```bash
pip install -r requirements.txt
```

### 4. Run the Simulation
Once setup is complete, start the simulation with:
```bash
python main.py
```

---

## 🎮 Controls

| Key | Action |
|-----|--------|
| **SPACE** | Deploy new hostile drones |
| **A** | Toggle AEGIS protocol ON/OFF |
| **D** | Toggle sensor/debug view |
| **T** | Toggle role display |
| **R** | Reset simulation |
| **ESC** | Exit application |

---

## 📂 Project Structure

```
aegis_drone_swarm/
├── simulation/
│   ├── models/
│   │   ├── drone.py          # Drone AI logic
│   │   └── world.py          # Environment
│   ├── simulation.py         # Core simulation engine
│   └── utils/                # Helper functions
├── main.py                   # Entry point
├── requirements.txt          # Dependencies
└── README.md                 # Documentation
```