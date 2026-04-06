from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route("/")
def home():
    return "AI Co-Pilot Backend Running"

if __name__ == "__main__":
    socketio.run(app, debug=True)
