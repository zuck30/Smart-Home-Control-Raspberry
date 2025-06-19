# Smart Home IoT System with Python

## Overview
This project simulates a Raspberry Pi-based smart home system controlling virtual devices (lights, fan, door sensor) and monitoring a temperature sensor. It features a clean Streamlit web interface with toggle switches, icons, and a responsive layout. MQTT enables IoT communication, with a mock mode for offline demos. Data is logged to CSV files. Fixed MQTT status display and device toggle issues.

## Features
- **Clean UI**: Modern dashboard with device cards, toggle switches, and icons.
- **Device Control**: Toggle Living Room Light, Bedroom Light, Ceiling Fan, and Front Door Sensor (pins 18, 19, 23, 24).
- **Sensor Monitoring**: Real-time temperature (24–26 °C) on pin 4 with a line chart.
- **MQTT**: IoT communication with mock mode if broker is unreachable.
- **Logging**: Saves actions and sensor data to CSV with download buttons.
- **System Status**: Shows MQTT connection and last update time.

## Setup Instructions
1. Ensure Anaconda is installed.
2. Activate environment:
   ```bash
   conda activate base
   ```
3. Install/upgrade dependencies:
   ```bash
   pip install streamlit paho-mqtt pandas --upgrade
   ```
4. Save `smart_home_streamlit.py` 
5. Run Streamlit, for me my computer path that i am working with is:
   ```bash
   cd /Users/sheldon/SmartHome
   streamlit run smart_home_streamlit.py
   ```
6. Access at `http://localhost:8502`.

## Dependencies
- Python 3.12 (Anaconda)
- `streamlit` (latest)
- `paho-mqtt` (latest)
- `pandas`


## Group Contributions

| S/N | FULL NAME                     | REGISTRATION NO |
|-----|-------------------------------|-----------------|
| 1   | ISSA KASSIM AMBARI            | T22-03-11780   |           
| 2   | KELVINI MASSAWE               | T22-03-05720   |           
| 3   | ADELA NOEL SANGIDA            | T22-03-01282   |           
| 4   | ALLY JANKS LUGE               | T22-03-00345   |           
| 5   | LIGHTNESS MSIGWA              | T22-03-00854   |           
| 6   | SHADRACK T JOHN               | T22-03-14609   |           
| 7   | FADHILI OMARY MSUYA           | T22-03-04742   |           
| 8   | HORMISDAS ONESPORY            | T22-03-06726   |           
| 9   | THERESIA FORTUNATUSI PYANKATI | T22-03-05368   |           
| 10  | BARAKA ANTHONY MALANDO        | T22-03-11790   |     