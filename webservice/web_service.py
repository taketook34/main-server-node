from webservice.state import server_data_struct

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse, StreamingResponse
import asyncio
import time
import cv2

app = FastAPI()

# Имитация получения кадров (замени на свою логику камеры)
def gen_frames():
    while True:
        frame = server_data_struct.last_frame
        if frame is None:
            time.sleep(0.01)
            continue
    
        ret, buffer = cv2.imencode('.jpg', frame)
        
        if not ret:
            continue # Если не удалось закодировать, пробуем следующий
            
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        time.sleep(0.03)  # Ограничиваем поток ~30 кадрами в секунду

@app.get("/")
async def get():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.post("/action/{mode}")
async def handle_action(mode: str):
    #print(f"Команда получена: Режим {mode}")
    if mode == 'N':
        server_data_struct.current_channel += 1
    if mode == "P":
        server_data_struct.current_channel -= 1
    return {"status": "success", "mode": mode}

@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    count = 0
    while True:
        await asyncio.sleep(1)
        count += 1
        await websocket.send_text(f"{server_data_struct.last_log}")
