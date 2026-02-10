import cv2
import numpy as np
import json, threading, socket

class VideoStreamManager:
    _window_name = "Camera stream"
    _client_manager = None
    _current_view = None
    _no_signal_screen = cv2.imread('examples/image.jpeg')
    _receiver_list = []
    _current_receiver = None
    _old_receiver_name = ''
    _is_running = False
    
    _udp_server_port = 5001
    _udp_server_max_packets = 65535
    _udp_server_sock = None

    _mqtt_client = None
    _mqtt_topic = None

    def __init__(self, client, topic, client_manager, udp_port = 5001):
        self._mqtt_client = client
        self._mqtt_topic = topic
        self._client_manager = client_manager
        self._receiver_list = self._client_manager.get_clients_list()
        self._current_receiver = self._receiver_list[0] if self._receiver_list else None

        # Set start image just for start
        self._udp_server_port = udp_port
        self._current_view = self._no_signal_screen
        self._udp_server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._udp_server_sock.bind(("0.0.0.0", self._udp_server_port))
        self._udp_server_sock.settimeout(0.05)

    def _fetch_actual_channels(self):
        self._receiver_list = self._client_manager.get_clients_list()

    def _sync_current_channel(self):
        # """Проверка актуальности выбранного канала."""
        if not self._receiver_list:
            self._current_receiver = None
            return
        if self._current_receiver not in self._receiver_list:
            print("Current channel are unavailable")
            
            if self._current_receiver is not None:
                try:
                    self._old_receiver_name = self._current_receiver.get_name()
                except Exception:
                    self._old_receiver_name = "unknown"
            else:
                self._old_receiver_name = "none"

            self._current_receiver = self._receiver_list[0]
            self._mqtt_switch()
        

    def _switch_next(self):
        """Going on next channel"""
        if not self._receiver_list:
            return

        try:
            curr_idx = self._receiver_list.index(self._current_receiver)
            next_idx = (curr_idx + 1) % len(self._receiver_list)
            self._old_receiver_name = self._current_receiver.get_name()
            self._current_receiver = self._receiver_list[next_idx]
            self._mqtt_switch()

        except ValueError:
            # Если канал пропал в момент нажатия, берем первый
            self._old_receiver_name = self._current_receiver.get_name()
            self._current_receiver = self._receiver_list[0]
            self._mqtt_switch()
        
        print(f"Switched to: {self._current_receiver.get_name()}")
    
    def _mqtt_switch(self):
        device_id = self._mqtt_client._client_id.decode('utf-8')
        stop_message = {'sender': device_id, 'receiver': self._old_receiver_name, 'command': 'STOP'}
        go_message = {'sender': device_id,
                      'receiver': self._current_receiver.get_name(),
                      'command': 'GO', "port": self._udp_server_port}
        self._mqtt_client.publish(self._mqtt_topic, json.dumps(stop_message))
        self._mqtt_client.publish(self._mqtt_topic, json.dumps(go_message))
    
    def start(self):
        self._is_running = True
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()

        # receive_thread = threading.Thread(target=self._get_messages, daemon=True)
        # receive_thread.start()
    
    # def _get_messages(self):
    #     while self._is_running:
    #         data, arr = self._udp_server_sock.recvfrom(self._udp_server_max_packets)
    #         nparr = np.frombuffer(data, np.uint8)
    #         img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    #         if img is not None:
    #             print("set image from")
    #             self._current_view = img

    def run(self):
        print("Starting video stream")
        while self._is_running:
            self._fetch_actual_channels()
            self._sync_current_channel()

            # if not self._current_receiver:
            #     self._current_view = self._no_signal_screen

            cv2.imshow(self._window_name, self._current_view)

            key = cv2.waitKey(100) & 0xFF

            if key == ord('n'):
                self._switch_next()
            elif key == ord('q'):
                # Вихід
                break

        cv2.destroyAllWindows()
    
    def __del__(self):
        self._is_running = False        

