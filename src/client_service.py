import threading, json, socket, logging

logger = logging.getLogger(__name__)

class Client:
    _name = None
    _id = None
    _deviceType = None
    _lastResponseTimeMs = 0
    _udp_server_socket = None
    _udp_server_port = 0
    # _udp_server_port = 0
    # _udp_server_addr = ''

    def __init__(self, nameString_, server_port_):
        self._name = nameString_
        client_info = self._name.split('_')
        self._id = client_info[1]
        self._deviceType = client_info[0]
        self._udp_server_port = server_port_
        self._udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._udp_server_socket.bind(("0.0.0.0", server_port_))
        logger.info(f"Socket for port {self._udp_server_port} created")
        #self._udp_server_sock.settimeout(0.05)
        # self._udp_server_port = server_port_
        # self._udp_server_addr = server_addr_

    def __str__(self):
        return self._name

    def get_name(self):
        return self._name
    
    def get_socket(self):
        return self._udp_server_socket
    
    def close_socket(self):
        self._udp_server_socket.close()
        logger.info(f"Socket for port {self._udp_server_port} closed")
    
    def get_deviceType(self):
        return self._deviceType

    def get_timer(self):
        return self._lastResponseTimeMs

    def reset_timer(self):
        self._lastResponseTimeMs = 0
    
    def increase_timer(self, time_ms=10):
        self._lastResponseTimeMs += time_ms
    
    def __del__(self):
        self.close_socket()

class ClientManager:
    ''' SQLITE3 ??? '''
    _clientsList = []
    _clientsLock = threading.Lock()
    _mqtt_client = None
    _mqtt_topic = ''
    _device_id = None
    _client_last_port = 5001

    def __init__(self, client, topic):
        self._mqtt_client = client
        self._mqtt_topic = topic
        self._device_id = self._mqtt_client._client_id.decode('utf-8')

    def check_client(self, check_name_):
        for client in self._clientsList:
            if check_name_ == client.get_name():
                # critical section
                with self._clientsLock:
                    client.reset_timer()
                return True

        return False

    def get_clients_list(self):
        return self._clientsList

    def show_clients_list(self, looking_type=None):
        if looking_type:
            return {client : client.get_timer() for client in self._clientsList if client.get_deviceType() == looking_type}
        else:
            return {client : client.get_timer() for client in self._clientsList}

    def add_client(self, new_name_):
        new_client = Client(new_name_, self._client_last_port)
        # critical section
        with self._clientsLock:
            self._clientsList.append(new_client)
            
            assoc_message = {'sender': self._device_id, 'receiver': new_name_, 'port': self._client_last_port}
            self._mqtt_client.publish(self._mqtt_topic, json.dumps(assoc_message))
        self._client_last_port += 1
    

    def increase_timers(self):
        for increasing_device in self._clientsList:
            # critical section
            with self._clientsLock:
                increasing_device.increase_timer()
    
    def del_client(self, client_delete):
        with self._clientsLock:
            self._clientsList.remove(client_delete)
        
        stop_message = {'sender': self._device_id, 'receiver': client_delete.get_name(), 'port': 0}
        self._mqtt_client.publish(self._mqtt_topic, json.dumps(stop_message))

    def cleanup(self):
        client_list_ = self._clientsList.copy()

        for client_delete in client_list_:
            logger.info(f"removing {client_delete.get_name()}")
            self.del_client(client_delete)

    def __del__(self):
        pass
        

