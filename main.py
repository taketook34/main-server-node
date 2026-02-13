import paho.mqtt.client as mqtt
import time, threading, json, os, signal, sys
from src.client_service import ClientManager
from src.video_render import videoPlayerTask
from src.device_info import MQTTManager
import netifaces

CLIENT_NAME = "PC_" + netifaces.ifaddresses('wlp98s0')[netifaces.AF_INET][0]['addr']
MANAGMENT_TOPIC = "test/topic"
broker = "192.168.0.104" # Можна замінити на IP твого ПК
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, CLIENT_NAME)
client_manager = ClientManager(client, MANAGMENT_TOPIC)
mqtt_manager = MQTTManager(client_manager, client)
program_stop_signal = threading.Event()

def signal_handler(sig, frame):
    print('\n[!] Get Ctrl+C! Closing work...')
    program_stop_signal.set()
    infoThread.join()
    videoPlayerThread.join()

    client_manager.cleanup()
    
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)

    #client.on_message = on_message
    client.connect(broker, 1883)
    client.subscribe(MANAGMENT_TOPIC)

    global infoThread
    global videoPlayerThread

    infoThread = threading.Thread(target=mqtt_manager.deviceInfoTask, args=(program_stop_signal,))
    infoThread.start()

    mqttLoopThread = threading.Thread(target=mqtt_manager.mqttLoopTask, args=(program_stop_signal,), daemon=True)
    mqttLoopThread.start()

    videoPlayerThread = threading.Thread(target=videoPlayerTask, args=(client_manager, program_stop_signal))
    videoPlayerThread.start()

    #client.loop_forever()

if __name__ == "__main__":
    main()
