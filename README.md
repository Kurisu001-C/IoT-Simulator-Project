# 🏠 IoT Simulator Project

ระบบจำลอง IoT ของ **Smart Home 4 ห้อง** (ห้องนั่งเล่น, ห้องนอน, ห้องครัว, ห้องน้ำ) ที่สร้างข้อมูลเซนเซอร์เสมือนจริง
ส่งผ่าน MQTT เก็บลงฐานข้อมูล และแสดงผลบน Dashboard โดยรันทั้งหมดด้วย Docker Compose คำสั่งเดียว
เหมาะสำหรับเรียนรู้สถาปัตยกรรม IoT โดยไม่ต้องมีอุปกรณ์จริง

## สถาปัตยกรรม

```
Python Simulators ──MQTT──► Mosquitto ──► Telegraf ──► InfluxDB ──► Grafana
 (4 ห้อง)                  (broker)     (subscribe    (เก็บข้อมูล)   (Dashboard)
                                         sensors/#)
```

| บริการ | หน้าที่ | พอร์ต |
|---|---|---|
| `mqtt` (Mosquitto) | MQTT Broker | 1883 (MQTT), 9001 (WebSocket) |
| `Smarthome` | รันสคริปต์จำลองเซนเซอร์ 4 ห้องด้วย Supervisor | 9997 (Supervisor Web UI) |
| `telegraf` | รับข้อมูลจากหัวข้อ `sensors/#` แล้วส่งเข้า InfluxDB ทุก 10 วินาที | — |
| `influxdb` | เก็บข้อมูล (org `VCUniv`, bucket `sensor_data`) | 8086 |
| `grafana` | Dashboard "SmartHome" (ตั้งค่าไว้ล่วงหน้า) | 3000 |

## ข้อมูลที่จำลอง

| ห้อง | MQTT Topic | ข้อมูล (JSON) | ส่งทุก |
|---|---|---|---|
| ห้องนั่งเล่น | `sensors/livingroom` | `temperature`, `humidity`, `light_lux`, `pm25` | 3 วินาที |
| ห้องนอน | `sensors/bedroom` | `temperature`, `humidity`, `co2_level`, `bed_occupancy` | 3 วินาที |
| ห้องครัว | `sensors/kitchen` | `temperature`, `humidity`, `fridge_temp`, `gas_leak_ppm` | 3 วินาที |
| ห้องน้ำ | `sensors/bathroom` | `temperature`, `humidity`, `water_flow_lpm`, `water_heater_temp`, `presence` | 10 วินาที |

ค่าเปลี่ยนแบบค่อยเป็นค่อยไปให้ดูสมจริง (เช่น ห้องน้ำจะสุ่มมีคนอาบน้ำ ทำให้ความชื้นและอุณหภูมิน้ำอุ่นเพิ่มขึ้น)

## วิธีรัน

**ต้องมี:** [Docker](https://www.docker.com/) และ Docker Compose

1. โคลน repo

   ```bash
   git clone https://github.com/Kurisu001-C/IoT-Simulator-Project.git
   cd IoT-Simulator-Project
   ```

2. สร้างไฟล์ `.env` (ถูก ignore ไว้ใน git) แล้วกำหนดค่าเอง

   ```env
   INFLUXDB_USER=admin
   INFLUXDB_PASS=ตั้งรหัสผ่านของคุณ
   INFLUXDB_TOKEN=ตั้ง-token-ของคุณ
   GRAFANA_USER=admin
   GRAFANA_PASS=ตั้งรหัสผ่านของคุณ
   ```

3. เริ่มระบบ

   ```bash
   docker compose up -d --build
   ```

4. เปิดดูผล

   - Grafana: http://localhost:3000 (ล็อกอินด้วย `GRAFANA_USER` / `GRAFANA_PASS`) → Dashboard **SmartHome**
   - InfluxDB: http://localhost:8086
   - Supervisor (จัดการสคริปต์จำลอง): http://localhost:9997

5. หยุดระบบ

   ```bash
   docker compose down        # เพิ่ม -v หากต้องการลบข้อมูลที่เก็บไว้
   ```

## โครงสร้างโปรเจกต์

```
.
├── docker-compose.yaml          # นิยามบริการทั้งหมด
├── dockerfile.simulator         # Image ของตัวจำลอง (Python + paho-mqtt + Supervisor)
├── supervisord.conf             # รันและรีสตาร์ทสคริปต์ sim_*.py อัตโนมัติ
├── sim_livingroom.py            # ตัวจำลองห้องนั่งเล่น
├── sim_bedroom.py               # ตัวจำลองห้องนอน
├── sim_kitchen.py               # ตัวจำลองห้องครัว
├── sim_bathroom.py              # ตัวจำลองห้องน้ำ
├── telegraf.conf                # MQTT → InfluxDB
├── config/mosquitto.conf        # ตั้งค่า MQTT Broker
└── grafana/                     # Datasource และ Dashboard ที่ตั้งไว้ล่วงหน้า
```

## หมายเหตุด้านความปลอดภัย

โปรเจกต์นี้ออกแบบมาเพื่อการเรียนรู้และทดลองในเครื่อง ค่าเริ่มต้นบางอย่างจึงไม่เหมาะกับการใช้งานจริง

- Mosquitto เปิด `allow_anonymous true`
- Supervisor Web UI (พอร์ต 9997) ใช้ผู้ใช้/รหัสผ่านเริ่มต้นที่ระบุไว้ใน `supervisord.conf`

หากเปิดให้เข้าถึงจากภายนอกเครื่อง ควรเปลี่ยนค่าเหล่านี้และไม่เปิดพอร์ตสู่อินเทอร์เน็ต
