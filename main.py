import paho.mqtt.client as mqtt
import threading, signal, sys, time
import netifaces
import logging
import uvicorn

from src.client_service import ClientManager
from src.video_render import videoPlayerTask
from src.device_info import MQTTManager

from webservice.state import server_data_struct
#from webservice.web_service import app

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


CLIENT_NAME = "PC_" + netifaces.ifaddresses('wlp98s0')[netifaces.AF_INET][0]['addr']
MANAGMENT_TOPIC = "test/topic"
broker = "192.168.0.104" # Можна замінити на IP твого ПК
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, CLIENT_NAME)
client_manager = ClientManager(client, MANAGMENT_TOPIC)
mqtt_manager = MQTTManager(client_manager, client)
program_stop_signal = threading.Event()

def signal_handler(sig, frame):
    logger.info('\n[!] Get Ctrl+C! Closing work...')
    program_stop_signal.set()
    infoThread.join()
    videoPlayerThread.join()

    client_manager.cleanup()
    sys.exit(0)

def run_fastapi():
    while True:
        logger.info(f"web info: {server_data_struct.last_log}")
        time.sleep(2)
    # uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None, log_level="info")

def main():
    signal.signal(signal.SIGINT, signal_handler)

    #client.on_message = on_message
    client.connect(broker, 1883)
    client.subscribe(MANAGMENT_TOPIC)

    logger.info(f"Subscribed and connected to ... MQTT broker {broker} and topic {MANAGMENT_TOPIC}")

    global infoThread
    global videoPlayerThread

    infoThread = threading.Thread(target=mqtt_manager.deviceInfoTask, args=(program_stop_signal, server_data_struct))
    infoThread.start()

    logger.info("Informational thread started")

    mqttLoopThread = threading.Thread(target=mqtt_manager.mqttLoopTask, args=(program_stop_signal,), daemon=True)
    mqttLoopThread.start()

    logger.info("MQTT messages handler started")

    videoPlayerThread = threading.Thread(target=videoPlayerTask, args=(client_manager, program_stop_signal, server_data_struct))
    videoPlayerThread.start()

    webPageThread = threading.Thread(target=run_fastapi, daemon=True, name="WebThread")
    webPageThread.start()

    #client.loop_forever()

if __name__ == "__main__":
    main()
