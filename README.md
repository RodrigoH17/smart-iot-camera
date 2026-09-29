# Smart IoT Camera

A low-cost smart surveillance camera prototype built with a Raspberry Pi Pico W, using MQTT to share sensor data and receive commands through a web dashboard accessible from anywhere.

Developed as the final project for the **Internet of Things** course at the Polytechnic Institute of Tomar (2024/2025).

---

## 📌 Project Overview

The device detects motion, switches automatically between day and night mode based on ambient light, and gives visual and sound feedback about its state. A web dashboard shows the live status and lets authorised users control the camera remotely.

Main features:

* Motion detection with a PIR sensor
* Automatic day/night mode using an LDR (calibrated threshold)
* Status feedback with an RGB LED, a mode LED and a buzzer
* Physical button to mute/unmute the sound
* MQTT communication with:

  * Keep Alive
  * Last Will and Testament (alerts on unexpected power loss)
  * Retained messages (dashboard always shows the last known state)
* Web dashboard over MQTT WebSockets:

  * Login with per-user permissions (enforced by the broker ACL)
  * Remote on/off and sound control
  * Light/dark theme that follows the device's day/night mode
* Remote access from anywhere using ngrok, despite private IPv4 addresses
* Real-time push notifications with ntfy.sh
* Wi-Fi provisioning: if the device can't connect, it starts a configuration portal (`PicoConfig` access point)

---

## 🔌 Hardware

| Component | Pico W pin |
|---|---|
| PIR motion sensor | GP0 |
| LDR light sensor | GP28 (ADC) |
| RGB LED (common anode) | GP10 (R), GP12 (G), GP11 (B) |
| Night mode LED | GP14 |
| Buzzer | GP17 (PWM) |
| Sound button | GP15 |

---

## 📂 Project Structure

```
firmware/   MicroPython code for the Pico W (main program and Wi-Fi provisioning)
web/        Web dashboard (login page and MQTT control panel)
testes/     Early hardware and MQTT test scripts
docs/       Project report (in Portuguese)
```

---

## ⚙️ Setup

Clone the repository:

```bash
git clone https://github.com/RodrigoH17/smart-iot-camera.git
cd smart-iot-camera
```

### Requirements

* Raspberry Pi Pico W with MicroPython
* MicroPython libraries on the device: `umqtt.simple` and `microdot`
* Mosquitto MQTT broker with a WebSockets listener, user accounts and an ACL file
* ngrok (to expose the broker and dashboard to the internet)

### Device

1. Copy `firmware/provisioning.py` to the Pico W
2. Copy `firmware/main_mqtt_camera.py` to the Pico W as `main.py` (so it runs on boot)
3. In `main.py`, set `MQTT_BROKER`, `MQTT_USER` and `MQTT_PASS` to match your broker

### Dashboard

1. Start ngrok and copy the public `wss://` address of the broker
2. Set it as `broker` in `web/index_mqtt_login.html`
3. Serve the `web/` folder:

```bash
cd web
python -m http.server 8080
```

---

## ▶️ Usage

1. Power on the Pico W. On first boot (or if the saved network fails), connect to the `PicoConfig` Wi-Fi network, open `http://192.168.4.1` and enter your Wi-Fi details, then restart the device
2. Open the dashboard at `http://localhost:8080/login.html` (or the ngrok address)
3. Log in and control the camera. The demo accounts are defined in `web/login.html` and must also exist in the Mosquitto password file

---

## 🧠 Technologies

* MicroPython (Raspberry Pi Pico W)
* MQTT (Mosquitto, umqtt.simple, MQTT.js)
* Microdot (provisioning web server)
* HTML, CSS and JavaScript
* ngrok
* ntfy.sh

---

## 📌 Notes

* The dashboard login is checked in the browser; the real access control is done by the MQTT broker (user accounts and ACL)
* The free version of ngrok generates a new address on every restart, so the broker address in the dashboard must be updated each time
* The interface and the report are in Portuguese

---

## 👨‍💻 Authors

Rodrigo Henriques
GitHub: https://github.com/RodrigoH17

Gonçalo Henriques
GitHub: https://github.com/goncalohenriques48

---
