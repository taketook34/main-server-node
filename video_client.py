import cv2
import numpy as np
import json, threading

class VideoStreamManager:
    _window_name = "Camera stream"
    _client_manager = None
    _current_view = None
    _black_screen = np.zeros((100, 100, 3), dtype=np.uint8)
    _receiver_list = []
    _current_receiver = None
    _old_receiver_name = ''
    _is_running = False

    _mqtt_client = None
    _mqtt_topic = None

    def __init__(self, client, topic, client_manager):
        self._mqtt_client = client
        self._mqtt_topic = topic
        self._client_manager = client_manager
        self._receiver_list = self._client_manager.get_clients_list()
        self._current_receiver = self._receiver_list[0] if self._receiver_list else None

        # Set start image just for start
        original_img = cv2.imread('examples/image.jpeg')
        self._current_view = original_img.copy()

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
        stop_message = {'sender': "Admin_Console", 'receiver': self._old_receiver_name, 'command': 'STOP'}
        go_message = {'sender': "Admin_Console", 'receiver': self._current_receiver.get_name(), 'command': 'GO'}
        self._mqtt_client.publish(self._mqtt_topic, json.dumps(stop_message))
        self._mqtt_client.publish(self._mqtt_topic, json.dumps(go_message))

    def process_input_image(self, client, userdata, msg):
        pass

        #self._current_view = original_img.copy()
    
    def start(self):
        self._is_running = True
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()

    def run(self):
        print("Starting video stream")
        while self._is_running:
            #print("video stream cycle")
            self._fetch_actual_channels()
            
            self._sync_current_channel()
            # Показуємо поточне зображення
            cv2.imshow(self._window_name, self._current_view)

            # Set label on picture
            #self._old_receiver = self._receiver_list[self._current_receiver]

            # Чекаємо натискання клавіші (0 означає чекати нескінченно)
            key = cv2.waitKey(50) & 0xFF

            if key == ord('n'):
                self._switch_next()

            elif key == ord('q'):
                # Вихід
                break

        cv2.destroyAllWindows()
    
    def __del__(self):
        self._is_running = False        

