# 🏍️ Moto Telemetry & AWS Project (Dinamo 400cc)

A modular Python telemetry system designed to analyze motorcycle riding dynamics using raw smartphone IMU/GPS data (via Phyphox). This project processes high-frequency sensor data to generate professional racing-style dashboards, calculate G-Forces, and assign a automated "Driver Profile" based on riding style.

## 🚀 Current Status: V1 (Local Analytics Engine)
The project currently operates as a robust local processing engine. It ingests raw XML data, applies advanced physics filtering, and outputs high-fidelity analytical dashboards.

### Core Features
* **Advanced Physics Engine:** Fuses 100Hz IMU data (Linear Acceleration) with 1Hz GPS data to calculate true torque (G-Force) and speed, avoiding common GPS averaging errors.
* **Dynamic Auto-Calibration:** Algorithm automatically calculates the phone's mounting angle on the motorcycle (baseline roll) to provide accurate lean angles without manual calibration.
* **Wrap-Around Protection:** Modular math implementation to prevent impossible angular jumps (gimbal lock effects) in lean calculations.
* **Driver Profile System:** Evaluates max lean, G-forces, and speed volatility to generate a "Safety Score" (0-100) and assigns a riding role (e.g., *Apex Predator*, *Steady Commuter*).
* **Visual Dashboard:** Uses Matplotlib to render a custom dark-mode map where route points scale dynamically based on G-Force intensity, pinpointing exact locations of max acceleration, braking, and top speed.

## 📂 Project Structure

```text
moto-telemetry-aws/
├── data/               # Raw .phyphox XML files (ignored by git)
├── exports/            # Generated dashboard PNGs (ignored by git)
├── src/
│   ├── core/           # Data parsing and physics math engine
│   ├── analysis/       # Driver profile logic and role matrices
│   └── visuals/        # Matplotlib dashboard and UI components
├── main.py             # Main orchestrator script
└── requirements.txt    # Project dependencies
```

🛠️ How to Run
Install dependencies: pip install -r requirements.txt

Place your raw Phyphox data file in the data/ folder.

Update the filename in main.py.

Run the engine: python main.py

Check the exports/ folder for your generated dashboard.

☁️ Roadmap: Phase 2 (AWS Cloud Integration)
The next major evolution of this project is migrating the local processing to a serverless AWS architecture:

[ ] AWS IoT Core: Direct telemetry streaming from the mobile device via MQTT.

[ ] AWS Lambda: Migrate the src/core/physics.py engine to serverless functions for real-time processing.

[ ] Amazon DynamoDB: Store processed ride metrics, max values, and historical Safety Scores.

[ ] Amazon QuickSight / Web App: Cloud-based frontend to replace local Matplotlib generation.
