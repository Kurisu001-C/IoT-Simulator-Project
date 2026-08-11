import paho.mqtt.client as mqtt
import json
import time
import random
import sys

node_name = "sensors/bathroom"
BROKER_IP = "mqtt-broker"
PORT = 1883
TOPIC = node_name

def smooth_change(current_val, min_val, max_val, max_step):
    step = random.uniform(-max_step, max_step)
    new_val = current_val + step
    if new_val < min_val: new_val = min_val
    if new_val > max_val: new_val = max_val
    return round(new_val, 1)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"🟢 [{node_name}] Successfully connected to MQTT Server!")
    else:
        print(f"🔴 [{node_name}] Connection failed. Error code: {rc}")

client = mqtt.Client(client_id="sim_bathroom")
client.on_connect = on_connect

try:
    client.connect(BROKER_IP, PORT, 60)
    client.loop_start() 
except Exception as e:
    print(f"Connection error: {e}", file=sys.stderr)
    sys.exit(0)

print(f"🚀 Starting data simulation for {node_name} (Press Ctrl+C to stop)")

# Initial values
temp = 28.0
hum = 65.0

try:
    while True:
        if not client.is_connected():
            print(f"🔴 [{node_name}] MQTT connection lost! Exiting with status 0 for Supervisor to restart.", file=sys.stderr)
            sys.exit(0)

        temp = smooth_change(temp, 25.0, 32.0, 0.3)
        
        is_showering = random.choices([True, False], weights=[10, 90])[0]
        
        if is_showering:
            hum = smooth_change(hum, 60.0, 95.0, 5.0) 
            water_flow = random.uniform(4.0, 8.0)
        else:
            hum = smooth_change(hum, 60.0, 95.0, 1.0)
            water_flow = 0.0

        data = {
            "temperature": temp,
            "humidity": hum,
            "water_flow_lpm": round(water_flow, 1),
            "presence": 1 if is_showering else 0
        }
        
        payload = json.dumps(data)
        client.publish(TOPIC, payload)
        print(f"📤 Data sent [{TOPIC}] -> {payload}")
        
        time.sleep(3)
        
except KeyboardInterrupt:
    print(f"\n🛑 Stopping {node_name}...")
    client.loop_stop()
    client.disconnect()
    print("Disconnected successfully")