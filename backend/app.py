from flask import Flask, jsonify
from flask_socketio import SocketIO
import time, threading
from train import Train

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# Create multiple trains
trains = [
    Train(train_id=1, speed=50),
    Train(train_id=2, speed=40),
    Train(train_id=3, speed=60)
]

@app.route("/api/train_status")
def train_status():
    return jsonify([{
        "train_id": train.train_id,
        "speed": train.speed,
        "position": train.position,
        "status": train.status
    } for train in trains])

def run_trains():
    while True:
        updates = []
        for train in trains:
            train.position += train.speed * 0.1
            updates.append({
                "train_id": train.train_id,
                "speed": train.speed,
                "position": train.position,
                "status": train.status
            })
        socketio.emit("train_update", updates)
        time.sleep(2)

threading.Thread(target=run_trains, daemon=True).start()

if __name__ == "__main__":
    socketio.run(app, debug=True)
