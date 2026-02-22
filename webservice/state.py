import threading
import logging

class WebDataStruct:
    
    last_frame = None
    current_channel = 0
    last_log = "Waiting for system log"

server_data_struct = WebDataStruct()