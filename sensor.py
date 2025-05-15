import paho.mqtt.publish as publish
import random
import time
import json

rooms = ["Room 1", "Room 2", "Room 3", "Room 4"]
broker = "broker.hivemq.com"

while True:
    for room in rooms:
        # Create a complete room data package
        room_data = {
            "temp": str(random.randint(20, 30)),
            "humidity": str(random.randint(30, 70)),
            "pressure": str(random.randint(980, 1050)),
            "airquality": random.choice(["good", "moderate", "poor"])
        }
        
        # Publish as a single JSON message
        publish.single(
            f"smartbuilding/{room.replace(' ', '')}",
            json.dumps(room_data),
            hostname=broker
        )
        
        print(f"[{room}] Published: {room_data}")
    time.sleep(5)