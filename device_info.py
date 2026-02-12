from client_service import ClientManager, Client
import time

def deviceInfoTask(client_manager_, stop_event):
    check_counter = 0
    while not stop_event.is_set():
        client_manager_.increase_timers()
        time.sleep(0.01)
        check_counter += 1

        if check_counter == 100:
            device_info = client_manager_.show_clients_list()
            for device in device_info.keys():
                print(f"Client {device}: {device_info[device]}ms; ", end="")
            print()
                
            for i in device_info.keys():
                if device_info[i] >= 1200:
                    client_manager_.del_client(i)
            
            check_counter = 0