from fastapi import FastAPI, WebSocket
from fastapi.responses import StreamingResponse, HTMLResponse, FileResponse
from webservice.state import server_data_struct
import asyncio
import os

app = FastAPI()

# Эндпоинт для главной страницы
@app.get("/")
async def index():
    # Путь к файлу index.html, который лежит в той же папке или рядом
    return FileResponse('templates/index.html')

@app.get("/video_feed")
async def video_feed():
    async def frame_generator():
        while True:
            if server_data_struct.last_frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + server_data_struct.last_frame + b'\r\n')
            await asyncio.sleep(0.04)
    return StreamingResponse(frame_generator(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/get_logs")
async def get_logs():
    # Просто возвращаем текущую строку из нашего хранилища
    return {"log": str(server_data_struct.last_log)}

@app.post("/next")
async def next_channel():
    server_data_struct.current_channel += 1
    return {"status": "ok", "channel": server_data_struct.current_channel}

@app.post("/prev")
async def prev_channel():
    if server_data_struct.current_channel > 0:
        server_data_struct.current_channel -= 1
    return {"status": "ok", "channel": server_data_struct.current_channel}