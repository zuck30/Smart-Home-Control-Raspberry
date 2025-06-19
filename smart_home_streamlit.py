import streamlit as st
import time
import csv
import random
import paho.mqtt.client as mqtt
import pandas as pd
import os
import socket
import threading

# Thread-safe MQTT status flag
mqtt_status_flag = False
mqtt_status_lock = threading.Lock()

# Simulated GPIO library
class MockGPIO:
    OUTPUT = 'OUTPUT'
    HIGH = 1
    LOW = 0
    
    def __init__(self):
        self.pins = {}
    
    def setmode(self, mode):
        print(f"Set mode to {mode}")
    
    def setup(self, pin, mode):
        if pin not in self.pins:
            self.pins[pin] = {'mode': mode, 'state': self.LOW}
            print(f"Setup pin {pin} as {mode}")
    
    def output(self, pin, state):
        if pin not in self.pins:
            self.setup(pin, self.OUTPUT)
        self.pins[pin]['state'] = state
        st.session_state[f"{pin}_state"] = state
        print(f"Pin {pin} set to {'HIGH' if state == self.HIGH else 'LOW'}")
    
    def input(self, pin):
        if pin not in self.pins:
            self.setup(pin, self.OUTPUT)
        base_temp = 25.0 + random.uniform(-2.0, 2.0)
        return round(base_temp + random.uniform(-0.5, 0.5), 2)

GPIO = MockGPIO()

# MQTT setup
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC_CONTROL = "smart_home/control"
MQTT_TOPIC_SENSOR = "smart_home/sensor"

# Device configuration
devices = {
    'led1': {'pin': 18, 'state': GPIO.LOW, 'name': 'Living Room Light', 'icon': 'fa-lightbulb'},
    'led2': {'pin': 19, 'state': GPIO.LOW, 'name': 'Bedroom Light', 'icon': 'fa-lightbulb'},
    'fan': {'pin': 23, 'state': GPIO.LOW, 'name': 'Ceiling Fan', 'icon': 'fa-fan'},
    'door': {'pin': 24, 'state': GPIO.LOW, 'name': 'Front Door Sensor', 'icon': 'fa-door-open'}
}

# Data logging setup
LOG_FILE = "/Users/sheldon/Downloads/SmartHome/sensor_data.csv"
ACTION_LOG_FILE = "/Users/sheldon/Downloads/SmartHome/action_log.csv"

def init_csv():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Temperature'])
        print(f"Created {LOG_FILE}")
    if not os.path.exists(ACTION_LOG_FILE):
        with open(ACTION_LOG_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Device', 'Action'])
        print(f"Created {ACTION_LOG_FILE}")

# MQTT callbacks
def on_connect(client, userdata, flags, rc, *args, **kwargs):
    global mqtt_status_flag
    if rc == 0:
        print(f"Connected to MQTT broker with code {rc}")
        client.subscribe(MQTT_TOPIC_CONTROL)
        with mqtt_status_lock:
            mqtt_status_flag = True
    else:
        print(f"Failed to connect to MQTT broker with code {rc}")
        with mqtt_status_lock:
            mqtt_status_flag = False

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"Received MQTT message: {payload}")
    try:
        device, state = payload.split(':')
        state = GPIO.HIGH if state == 'ON' else GPIO.LOW
        if device in devices and devices[device]['state'] != state:
            devices[device]['state'] = state
            GPIO.output(devices[device]['pin'], state)
            log_action(device, 'ON' if state == GPIO.HIGH else 'OFF')
    except Exception as e:
        print(f"Error processing MQTT message: {e}")

# MQTT client setup
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def test_broker_connectivity():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((MQTT_BROKER, MQTT_PORT))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"Broker connectivity test failed: {e}")
        return False

def start_mqtt():
    if test_broker_connectivity():
        try:
            mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
            mqtt_client.loop_start()
            print("MQTT started")
        except Exception as e:
            print(f"MQTT connection failed: {e}")
            with mqtt_status_lock:
                mqtt_status_flag = False
            st.session_state['mock_mqtt'] = True
    else:
        print("MQTT broker unreachable; using mock mode")
        with mqtt_status_lock:
            mqtt_status_flag = False
        st.session_state['mock_mqtt'] = True

# Log actions
def log_action(device, action):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(ACTION_LOG_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, device, action])
        print(f"Logged action: {device} {action}")
    except Exception as e:
        print(f"Error logging action: {e}")

# Update sensor data
def update_sensor():
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    temp = GPIO.input(4)
    print(f"Sensor reading: {temp:.2f} °C at {timestamp}")
    try:
        with open(LOG_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, f"{temp:.2f}"])
        if not st.session_state.get('mock_mqtt', False):
            mqtt_client.publish(MQTT_TOPIC_SENSOR, f"Temperature:{temp:.2f}")
        st.session_state['latest_temp'] = temp
        st.session_state['temp_data'].append({'Timestamp': timestamp, 'Temperature': temp})
        if len(st.session_state['temp_data']) > 50:
            st.session_state['temp_data'].pop(0)
        st.session_state['last_update'] = timestamp
    except Exception as e:
        print(f"Error updating sensor: {e}")

# Simulated GPIO setup
def setup_gpio():
    GPIO.setmode('BCM')
    for device in devices:
        GPIO.setup(devices[device]['pin'], GPIO.OUTPUT)
    GPIO.setup(4, GPIO.OUTPUT)
    print("GPIO setup complete")

# Streamlit app
def main():
    st.set_page_config(page_title="Smart Home Control", layout="wide")
    
    # Custom CSS
    st.markdown("""
        <style>
        .header {
            background-color: #2c3e50;
            color: white;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            margin-bottom: 20px;
        }
        .device-card {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
            margin: 10px;
            text-align: center;
            transition: transform 0.2s;
        }
        .device-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .status-on { color: #28a745; font-weight: bold; }
        .status-off { color: #dc3545; font-weight: bold; }
        .status-dot-on { height: 10px; width: 10px; background-color: #28a745; border-radius: 50%; display: inline-block; }
        .status-dot-off { height: 10px; width: 10px; background-color: #dc3545; border-radius: 50%; display: inline-block; }
        .temp-display {
            font-size: 2.5em;
            color: #007bff;
            text-align: center;
            margin: 10px 0;
        }
        .download-btn {
            background-color: #007bff;
            color: white;
            border-radius: 5px;
            padding: 8px 16px;
            text-decoration: none;
        }
        .download-btn:hover {
            background-color: #0056b3;
        }
        </style>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
        <div class='header'>
            <h2><i class='fas fa-home'></i> Smart Home Control System</h2>
            <p>Simulated Raspberry Pi IoT Solution</p>
        </div>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'temp_data' not in st.session_state:
        st.session_state['temp_data'] = []
    if 'latest_temp' not in st.session_state:
        st.session_state['latest_temp'] = 0.0
    if 'last_sensor_update' not in st.session_state:
        st.session_state['last_sensor_update'] = 0
    if 'last_update' not in st.session_state:
        st.session_state['last_update'] = "N/A"
    if 'mock_mqtt' not in st.session_state:
        st.session_state['mock_mqtt'] = False
    for device in devices:
        if f"{devices[device]['pin']}_state" not in st.session_state:
            st.session_state[f"{devices[device]['pin']}_state"] = GPIO.LOW

    # Update MQTT status from flag
    with mqtt_status_lock:
        st.session_state['mqtt_status'] = mqtt_status_flag

    # Update sensor periodically
    if time.time() - st.session_state['last_sensor_update'] > 5:
        update_sensor()
        st.session_state['last_sensor_update'] = time.time()
        st.rerun()

    # Main layout
    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("Device Control")
        device_cols = st.columns(2)
        for i, (device, info) in enumerate(devices.items()):
            with device_cols[i % 2]:
                state_label = 'OPEN' if device == 'door' and info['state'] == GPIO.HIGH else 'CLOSED' if device == 'door' else 'ON' if info['state'] == GPIO.HIGH else 'OFF'
                st.markdown(f"""
                    <div class='device-card'>
                        <i class='fas {info['icon']} fa-2x'></i>
                        <h4>{info['name']}</h4>
                        <p>
                            <span class='status-dot-{'on' if info['state'] == GPIO.HIGH else 'off'}'></span>
                            {state_label}
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                toggle = st.toggle(
                    label=f"Toggle {info['name']}",
                    value=info['state'] == GPIO.HIGH,
                    key=f"toggle_{device}",
                    label_visibility="hidden"
                )
                if toggle != (info['state'] == GPIO.HIGH):
                    new_state = GPIO.HIGH if toggle else GPIO.LOW
                    devices[device]['state'] = new_state
                    GPIO.output(info['pin'], new_state)
                    action = 'ON' if new_state == GPIO.HIGH else 'OFF'
                    print(f"Toggle {device} to {action}")
                    if not st.session_state.get('mock_mqtt', False):
                        mqtt_client.publish(MQTT_TOPIC_CONTROL, f"{device}:{action}")
                    log_action(device, action)
                    st.rerun()

    with col2:
        st.subheader("Environment Monitoring")
        st.markdown(f"""
            <div class='temp-display'>
                <i class='fas fa-thermometer-half'></i> {st.session_state['latest_temp']:.2f} °C
            </div>
        """, unsafe_allow_html=True)
        
        st.subheader("Temperature History")
        if st.session_state['temp_data']:
            df = pd.DataFrame(st.session_state['temp_data'])
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
            st.line_chart(df.set_index('Timestamp')['Temperature'], height=200)

        st.subheader("System Status")
        status_color = "#28a745" if st.session_state['mqtt_status'] else "#dc3545"
        status_text = "Connected" if st.session_state['mqtt_status'] else "Disconnected (Mock Mode)" if st.session_state.get('mock_mqtt', False) else "Disconnected"
        st.markdown(f"""
            <p><b>MQTT:</b> <span style='color:{status_color}'>{status_text}</span></p>
            <p><b>Last Update:</b> {st.session_state['last_update']}</p>
        """, unsafe_allow_html=True)

    # Logs and downloads
    with st.expander("View Action Logs & Downloads"):
        st.subheader("Recent Actions")
        if os.path.exists(ACTION_LOG_FILE):
            df_actions = pd.read_csv(ACTION_LOG_FILE)
            st.dataframe(df_actions.tail(10), use_container_width=True)
        
        st.subheader("Download Logs")
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, 'rb') as f:
                    st.download_button("Sensor Data", f, file_name="sensor_data.csv", use_container_width=True)
        with col_dl2:
            if os.path.exists(ACTION_LOG_FILE):
                with open(ACTION_LOG_FILE, 'rb') as f:
                    st.download_button("Action Log", f, file_name="action_log.csv", use_container_width=True)

    # Start MQTT
    if 'mqtt_started' not in st.session_state:
        setup_gpio()
        start_mqtt()
        st.session_state['mqtt_started'] = True

if __name__ == "__main__":
    main()