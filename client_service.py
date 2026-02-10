import threading

class Client:
    _name = None
    _id = None
    _deviceType = None
    _lastResponseTimeMs = 0

    def __init__(self, nameString_):
        self._name = nameString_
        client_info = self._name.split('_')
        self._id = client_info[1]
        self._deviceType = client_info[0]

    def __str__(self):
        return self._name

    def get_name(self):
        return self._name
    
    def get_id(self):
        return self._id
    
    def get_deviceType(self):
        return self._deviceType

    def get_timer(self):
        return self._lastResponseTimeMs

    def reset_timer(self):
        self._lastResponseTimeMs = 0
    
    def increase_timer(self):
        self._lastResponseTimeMs += 10


class ClientManager:
    ''' SQLITE3 ??? '''
    _clientsList = []
    _clientsLock = threading.Lock()

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
        new_client = Client(new_name_)
        # critical section
        with self._clientsLock:
            self._clientsList.append(new_client)
    

    def increase_timers(self):
        for increasing_device in self._clientsList:
            # critical section
            with self._clientsLock:
                increasing_device.increase_timer()
    
    def del_client(self, client_delete):
        with self._clientsLock:
            self._clientsList.remove(client_delete)

