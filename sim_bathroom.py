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
water_heater_temp = 28.0  # เริ่มต้นที่อุณหภูมิห้อง
water_ticks_left = 0      # จำนวนรอบ (รอบละ 10 วินาที) ที่จะเปิดน้ำค้างไว้

try:
    while True:
        if not client.is_connected():
            print(f"🔴 [{node_name}] MQTT connection lost! Exiting with status 0 for Supervisor to restart.", file=sys.stderr)
            sys.exit(0)

        # อุณหภูมิห้องเปลี่ยนแปลงเล็กน้อย
        temp = smooth_change(temp, 25.0, 32.0, 0.3)
        
        # จัดการสถานะการเปิด/ปิดน้ำให้เป็นธรรมชาติ
        if water_ticks_left > 0:
            water_ticks_left -= 1
            is_showering = True
        else:
            # โอกาส 10% ที่จะมีคนเริ่มอาบน้ำ
            if random.choices([True, False], weights=[10, 90])[0]:
                # สุ่มระยะเวลาเปิดน้ำ: 2 ถึง 12 รอบ (เท่ากับ 20 ถึง 120 วินาที)
                water_ticks_left = random.randint(2, 12)
                is_showering = True
            else:
                is_showering = False
        
        # อัปเดตค่าต่างๆ ตามสถานะการเปิดน้ำ
        if is_showering:
            # ความชื้นเพิ่มสูงขึ้นอย่างรวดเร็วขณะอาบน้ำ
            hum = smooth_change(hum + 2.0, 60.0, 95.0, 1.5) 
            water_flow = random.uniform(4.0, 8.0)
            
            # เครื่องทำน้ำอุ่นทำงาน (ร้อนขึ้นจนถึงช่วง 35-42 องศา)
            if water_heater_temp < 35.0:
                water_heater_temp += random.uniform(1.5, 3.0) # ร้อนขึ้นเร็ว
            else:
                water_heater_temp = smooth_change(water_heater_temp, 35.0, 42.0, 0.5)
        else:
            # ความชื้นค่อยๆ ลดลงกลับสู่สภาวะปกติ (ประมาณ 60)
            hum = smooth_change(hum - 0.5, 60.0, 95.0, 0.5)
            water_flow = 0.0
            
            # อุณหภูมิน้ำอุ่นจะค่อยๆ เย็นลงจนเท่ากับอุณหภูมิห้อง
            if water_heater_temp > temp:
                water_heater_temp -= random.uniform(0.5, 1.5)
                if water_heater_temp < temp:
                    water_heater_temp = temp

        data = {
            "temperature": round(temp, 1),
            "humidity": round(hum, 1),
            "water_flow_lpm": round(water_flow, 1),
            "water_heater_temp": round(water_heater_temp, 1),
            "presence": 1 if is_showering else 0
        }
        
        payload = json.dumps(data)
        client.publish(TOPIC, payload)
        print(f"📤 Data sent [{TOPIC}] -> {payload}")
        
        time.sleep(10)
        
except KeyboardInterrupt:
    print(f"\n🛑 Stopping {node_name}...")
    client.loop_stop()
    client.disconnect()
    print("Disconnected successfully")