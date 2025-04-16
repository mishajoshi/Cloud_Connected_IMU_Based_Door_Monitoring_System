import json
import ssl
import paho.mqtt.client as mqtt
from config import AWS_ENDPOINT, MQTT_PORT, KEEPALIVE, TOPIC, ROOT_CA, CERTIFICATE_PATH, PRIVATE_KEY_PATH

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to AWS IoT MQTT Broker successfully")
        client.subscribe(TOPIC)
    else:
        print("Failed to connect, return code %d" % rc)

def on_message(client, userdata, msg):
    socketio_instance = userdata.get("socketio")
    try:
        data = json.loads(msg.payload.decode())
        door_state = data.get("Door State", data.get("door_state", "Unknown"))
        timestamp = data.get("timestamp", 0)
        if socketio_instance:
            socketio_instance.emit("door_update", {"door_state": door_state, "timestamp": timestamp})
        print(f"MQTT Message received: {data}")
    except Exception as e:
        print("Error processing MQTT message:", e)

def start_mqtt(socketio_instance):
    client = mqtt.Client(userdata={"socketio": socketio_instance})
    client.on_connect = on_connect
    client.on_message = on_message

    client.tls_set(
        ca_certs=ROOT_CA,
        certfile=CERTIFICATE_PATH,
        keyfile=PRIVATE_KEY_PATH,
        tls_version=ssl.PROTOCOL_TLSv1_2
    )

    try:
        client.connect(AWS_ENDPOINT, MQTT_PORT, KEEPALIVE)
    except Exception as e:
        print("Could not connect to MQTT broker:", e)
        return

    client.loop_start() 
    print("MQTT client loop started")
