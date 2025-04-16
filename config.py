import os
from dotenv import load_dotenv

load_dotenv()

AWS_ENDPOINT = os.environ["AWS_ENDPOINT"]
MQTT_PORT = int(os.environ["MQTT_PORT"])
TOPIC = os.environ["TOPIC"]
CLIENT_ID = os.environ["CLIENT_ID"]
KEEPALIVE = int(os.environ["KEEPALIVE"])

ROOT_CA = os.environ["ROOT_CA"]
CERTIFICATE_PATH = os.environ["CERTIFICATE_PATH"]
PRIVATE_KEY_PATH = os.environ["PRIVATE_KEY_PATH"]

SECRET_KEY = os.environ["SECRET_KEY"]