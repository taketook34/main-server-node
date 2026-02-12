import cv2
import socket
import numpy as np

def videoPlayerTask(client_manager, stop_event):
    current_idx = 0
    window_name = 'UDP Stream Player'
    cv2.namedWindow(window_name)

    print("\'n\' - forward, \'p\' - back, \'q\' - quit")

    while not stop_event.is_set():
        # 1. Получаем актуальный список клиентов
        clients = client_manager.get_clients_list()
        
        if not clients:
            # Если список пуст, рисуем заглушку и ждем
            black_screen = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(black_screen, "No active clients...", (180, 240), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            cv2.imshow(window_name, black_screen)
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
            continue

        # 2. Корректируем индекс (на случай, если клиентов стало меньше)
        current_idx = current_idx % len(clients)
        
        # 3. Достаем сокет из текущего клиента
        current_client = clients[current_idx]
        active_socket = current_client.get_socket()
        active_socket.settimeout(0.05) # Минимальный таймаут для плавности

        try:
            # Читаем данные из UDP
            data, _ = active_socket.recvfrom(65536)
            
            # Декодируем JPEG/PNG в картинку OpenCV
            frame_arr = np.frombuffer(data, dtype=np.uint8)
            frame = cv2.imdecode(frame_arr, cv2.IMREAD_COLOR)

            if frame is not None:
                # Добавим текст, какой канал сейчас смотрим
                cv2.putText(frame, f"Channel: {current_idx}", (20, 40), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.imshow(window_name, frame)
                
        except (socket.timeout, socket.error):
            # Если данных нет, просто показываем черный экран с номером канала
            loading_screen = np.zeros((320, 240), dtype=np.uint8)
            cv2.putText(loading_screen, f"Connecting to Ch {current_idx}...", (20, 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
            cv2.imshow(window_name, loading_screen)

        # 4. Логика переключения
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('n'): # Next
            current_idx = (current_idx + 1) % len(clients)
        elif key == ord('p'): # Previous
            current_idx = (current_idx - 1) % len(clients)

    cv2.destroyAllWindows()