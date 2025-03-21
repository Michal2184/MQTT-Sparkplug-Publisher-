# 🛠️ Sparkplug Debugger Tool for AVEVA OI.MQTT

This is a lightweight GUI application built to assist with debugging and validating **Sparkplug B** payloads over MQTT, especially in environments using the **AVEVA OI.MQTT driver**.

## 🚀 Features

- ✅ Send **NBIRTH** and **DBIRTH** messages in valid Sparkplug B format
- 🔄 Auto-send **DBIRTH** on a configurable interval
- ✍️ Manually define metric values for `Pressure`, `Temperature`, and `FlowRate`
- 📂 Save and load MQTT and payload configurations
- 🔐 Supports username/password authentication and TLS encryption
- 👁️ Preview payload as JSON before sending
- 🧪 Compatible with **Mosquitto Broker** and **AVEVA OI.MQTT Driver**

## 🧰 Requirements

- Python 3.9+
- MQTT Broker (e.g. [Mosquitto](https://mosquitto.org/))
- AVEVA OI.MQTT Driver 
- Dependencies (install via pip):

```bash
pip install pysparkplug paho-mqtt


## 📬 License

This project is provided as-is for SCADA testing and educational purposes.
