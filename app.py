import os
from dotenv import load_dotenv

load_dotenv()

import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO
from mqtt_client import start_mqtt

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
socketio = SocketIO(app, async_mode='eventlet')

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    start_mqtt(socketio)
    socketio.run(app, debug=True, use_reloader=False)