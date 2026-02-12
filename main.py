import paho.mqtt.client as mqtt
import time, threading, json, os, signal, sys
from client_service import ClientManager
from video_render import videoPlayerTask
from device_info import deviceInfoTask
import netifaces

CLIENT_NAME = "PC_" + netifaces.ifaddresses('wlp98s0')[netifaces.AF_INET][0]['addr']
MANAGMENT_TOPIC = "test/topic"
broker = "192.168.0.104" # Можна замінити на IP твого ПК
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, CLIENT_NAME)
client_manager = ClientManager(client, MANAGMENT_TOPIC)
program_stop_signal = threading.Event()

def signal_handler(sig, frame):
    print('\n[!] Get Ctrl+C! Closing work...')
    program_stop_signal.set()
    infoThread.join()
    videoPlayerThread.join()
    del client_manager
    sys.exit(0)

def on_message(client, userdata, msg):
    payload_str = msg.payload.decode("utf-8")
    #print(payload_str)
    data = json.loads(payload_str)
    #print(data)

    sender = data.get('sender')
    if "CAM_" in sender:
        #print(payload_str)
        if not client_manager.check_client(sender):
            client_manager.add_client(sender)

def main():
    signal.signal(signal.SIGINT, signal_handler)

    client.on_message = on_message
    client.connect(broker, 1883)
    client.subscribe(MANAGMENT_TOPIC)

    global infoThread
    global videoPlayerThread

    infoThread = threading.Thread(target=deviceInfoTask, args=(client_manager, program_stop_signal), daemon=True)
    infoThread.start()

    videoPlayerThread = threading.Thread(target=videoPlayerTask, args=(client_manager, program_stop_signal), daemon=True)
    videoPlayerThread.start()

    client.loop_forever()

if __name__ == "__main__":
    main()
