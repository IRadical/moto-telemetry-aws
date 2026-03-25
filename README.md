# AWS IoT Motorcycle Telemetry System

An end-to-end IoT pipeline that simulates motorcycle physics, ingests telemetry via MQTT (mTLS), stores it in a NoSQL database, and provides real-time monitoring and analytics.

## 🚀 System Architecture
* **Edge (Python):** Realistic physics simulation (Lean angle, G-Force, Speed).
* **Ingestion (AWS IoT Core):** Secure mTLS connection using X.509 certificates.
* **Storage (Amazon DynamoDB):** High-velocity NoSQL storage for telemetry packets.
* **Live Monitor:** CLI-based real-time dashboard via Boto3.
* **Analytics Layer:** Automated session summaries and CSV export for data science.

## 🛠️ Project Structure
* `src/main.py`: Physics simulator and MQTT bridge.
* `src/connector.py`: AWS IoT Core secure connection logic.
* `src/monitor.py`: Real-time cloud-to-client dashboard.
* `src/analytics.py`: Session performance reporter.
* `src/export_data.py`: CSV data extractor.

## 📊 Sample Telemetry Data
| Speed (km/h) | Lean Angle (°) | G-Force (G) |
|--------------|----------------|-------------|
| 94.7         | 54.7           | 1.50        |
