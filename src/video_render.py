import cv2
import socket
import numpy as np
import logging

logger = logging.getLogger(__name__)


def videoPlayerTask(client_manager, stop_event, state_struct):
    current_idx = 0
    logger.info("\'n\' - forward, \'p\' - back, \'q\' - quit")
    state_struct.current_channel = current_idx

    while not stop_event.is_set():
        clients = client_manager.get_clients_list()
        
        if not clients:
            black_screen = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(black_screen, "No active clients...", (180, 240), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
            continue

        current_idx = state_struct.current_channel
        current_idx = current_idx % len(clients)
        current_client = clients[current_idx]
        active_socket = current_client.get_socket()
        active_socket.settimeout(0.05)

        try:
            data, _ = active_socket.recvfrom(65536)
            
            frame_arr = np.frombuffer(data, dtype=np.uint8)
            frame = cv2.imdecode(frame_arr, cv2.IMREAD_COLOR)

            if frame is not None:
                cv2.putText(frame, f"Channel: {current_idx}", (20, 40), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                state_struct.last_frame = frame
                
        except (socket.timeout, socket.error):
            loading_screen = np.zeros((320, 240), dtype=np.uint8)
            cv2.putText(loading_screen, f"Connecting to Ch {current_idx}...", (20, 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
            state_struct.last_frame = loading_screen

    logger.info("Closing  CV window")