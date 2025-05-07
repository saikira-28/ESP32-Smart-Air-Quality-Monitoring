# 🌿 Smart Air Quality Monitoring System

A complete end-to-end IoT pipeline to monitor and analyze indoor and outdoor air quality using ESP32, Telegraf, InfluxDB, and Grafana.

---

## 📦 Repository Contents

| File/Folder              | Description                                                      |
| ------------------------ | ---------------------------------------------------------------- |
| `arduino_code.ino`       | Code for ESP32 to collect and publish sensor data via MQTT       |
| `telegraf.conf`          | Telegraf configuration to consume MQTT data and send to InfluxDB |
| `grafana_dashboard.json` | Pre-built Grafana dashboard with dynamic visualizations          |
| `screenshots/`           | Images showing setup from ESP32 to final Grafana visualization   |

---

## 🌐 Project Overview

This project demonstrates an IoT-based solution to monitor:

* CO₂ concentration (`co2_ppm`)
* Temperature (`°C`)
* Humidity (`%`)

Additional sensor support (like PMS for PM2.5) is planned for future expansion.

The system distinguishes between **indoor** and **outdoor** environments dynamically and updates visualization accordingly.

---

## 🔗 Tech Stack

* **ESP32 DevKit V1** – Sensor data acquisition and MQTT publishing
* **MQTT Broker (e.g., Mosquitto)** – Message transport
* **Telegraf** – MQTT to InfluxDB data bridge
* **InfluxDB 2.x** – Time-series database
* **Grafana** – Real-time dashboards and visualizations

---

## 📊 Grafana Visualizations

1. **CO₂ Trends**: Line chart showing CO₂ levels over time (by location)
2. **Humidity vs Temperature**: Multi-axis chart with dual field analysis
3. **Dynamic Insights**:

   * Ice or matchstick tests for temperature detection
   * Location-aware PM2.5 sensor support (future-ready)

---

## 🚀 Getting Started

### 1. Flash ESP32

Upload `arduino_code.ino` to your ESP32 after configuring Wi-Fi and MQTT broker credentials.

### 2. Start MQTT Broker

Use Mosquitto or any MQTT broker on your machine or network.

```bash
mosquitto -v
```

### 3. Configure Telegraf

Copy `telegraf.conf` and run:

```bash
telegraf --config telegraf.conf
```

### 4. InfluxDB Setup

* Create a bucket named `airquality_data`
* Use token and org info in Telegraf config

### 5. Import Grafana Dashboard

* Open Grafana
* Import `grafana_dashboard.json`
* Verify data flow and visuals

---

## 📸 Screenshots

All screenshots related to the pipeline can be found in `/screenshots/`:

* ESP32 Serial Output
* MQTT Message Log
* Telegraf Console Logs
* InfluxDB Data View
* Grafana Dashboards
