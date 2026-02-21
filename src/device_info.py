from src.client_service import ClientManager, Client
import time, json
import logging

logger = logging.getLogger(__name__)

class MQTTManager:
    def __init__(self, client_manager, mqtt_client):
        self._mqtt_client = mqtt_client
        self._client_manager = client_manager
        # self._stop_event = stop_event

        self._mqtt_client.on_message = self._on_message
    
    def _on_message(self, client, userdata, msg):
        payload_str = msg.payload.decode("utf-8")
        #print(payload_str)
        data = json.loads(payload_str)
        #print(data)

        sender = data.get('sender')
        if "CAM_" in sender:
            #print(payload_str)
            if not self._client_manager.check_client(sender):
                self._client_manager.add_client(sender)

    def mqttLoopTask(self, stop_event):
        self._mqtt_client.loop_forever()
    
    def deviceInfoTask(self, stop_event):
        check_counter = 0
        while not stop_event.is_set():
            self._client_manager.increase_timers()
            time.sleep(0.01)
            check_counter += 1

            if check_counter == 100:
                device_info = self._client_manager.show_clients_list()
                clients_list_string = "clients list [ "
                for device in device_info.keys():
                    clients_list_string += f"Client {device}: {device_info[device]}ms; "
                clients_list_string += "]"
                logger.info(clients_list_string)
                    
                for i in device_info.keys():
                    if device_info[i] >= 1200:
                        self._client_manager.del_client(i)
                
                check_counter = 0
            
        logger.info("Closing receiving info from devices")
