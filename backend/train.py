import time
import threading

class Train:
    def __init__(self, train_id, speed=50, position=0, status="running"):
        self.train_id = train_id
        self.speed = speed
        self.position = position
        self.status = status

    def move(self):
        while True:
            self.position += self.speed * 0.1  # move every tick
            time.sleep(1)
