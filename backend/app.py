import threading

from flask import Flask, jsonify
from flask_cors import CORS
from train import Train

app = Flask(__name__)
CORS(app)  # allow requests from React frontend

train1 = Train(train_id=1, speed=50)
def run_train():
    train1.move()

threading.Thread(target=run_train, daemon=True).start()

@app.route("/api/train_status")
def train_status():
    return jsonify({
        "train_id": train1.train_id,
        "speed": train1.speed,
        "position": train1.position,
        "status": train1.status
    })


if __name__ == "__main__":
    app.run(debug=True)
