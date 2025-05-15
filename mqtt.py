import paho.mqtt.client as mqtt
import json

shared_data = {f"Room {i}": {} for i in range(1, 5)}

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribe to all room topics
    for room in ["Room1", "Room2", "Room3", "Room4"]:
        client.subscribe(f"smartbuilding/{room}")

def on_message(client, userdata, msg):
    try:
        room = msg.topic.split('/')[-1]
        room_name = f"Room {room[-1]}"  # Convert "Room1" to "Room 1"
        data = json.loads(msg.payload.decode())
        shared_data[room_name] = data
        print(f"Updated {room_name}: {data}")
    except Exception as e:
        print(f"Error processing message: {e}")

def start_subscriber():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    client.connect("broker.hivemq.com", 1883, 60)
    client.loop_start()