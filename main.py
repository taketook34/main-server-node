import paho.mqtt.client as mqtt
import time, threading, json, os
from client_service import *
from video_client import VideoStreamManager
import cv2
import netifaces

CLIENT_NAME = "PC_" + netifaces.ifaddresses('wlp98s0')[netifaces.AF_INET][0]['addr']
MANAGMENT_TOPIC = "test/topic"
#CAMERAIMAGE_TOPIC = "test/images"
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, CLIENT_NAME)
client_manager = ClientManager()
video_manager = VideoStreamManager(client, MANAGMENT_TOPIC, client_manager)


def lastMessageCheckTask():
    while True:
        client_manager.increase_timers()
        time.sleep(0.01)

def deviceInfoTask():
    while True:
        time.sleep(1)
        device_info = client_manager.show_clients_list()
        for device in device_info.keys():
            print(f"Client {device}: {device_info[device]}ms; ", end="")
            
        print()    
        for i in device_info.keys():
            if device_info[i] >= 1200:
                client_manager.del_client(i)  
    
def on_message(client, userdata, msg):
    pass


def process_managment_data(client, userdata, msg):
    payload_str = msg.payload.decode("utf-8")
    #print(payload_str)
    data = json.loads(payload_str)
    #print(data)

    sender = data.get('sender')
    if "CAM_" in sender:
        #print(payload_str)
        if not client_manager.check_client(sender):
            client_manager.add_client(sender)
    #data = json.loads(payload_str)

    # print(data['sender'])
    # print(data['message'])

def main():
    broker = "192.168.0.104" # Можна замінити на IP твого ПК

    client.on_message = on_message
    client.message_callback_add(MANAGMENT_TOPIC, process_managment_data)
    #client.message_callback_add(CAMERAIMAGE_TOPIC, video_manager.process_input_image)
    client.connect(broker, 1883)
    client.subscribe(MANAGMENT_TOPIC)
    #client.subscribe(CAMERAIMAGE_TOPIC)
    # client.subscribe(IMAGE_TOPIC)
    #client.publish(MANAGMENT_TOPIC, "hello there")

    infoThread = threading.Thread(target=deviceInfoTask, daemon=True)
    infoThread.start()

    lastMessageThread = threading.Thread(target=lastMessageCheckTask, daemon=True)
    lastMessageThread.start()

    video_manager.start()

    client.loop_forever()

if __name__ == "__main__":
    main()

# print("Сервер запущено. Надсилаю команду 'ON' в топік 'home/led'...")

# while True:
#     client.publish(MANAGMENT_TOPIC, "hi there")
#     time.sleep(1)
