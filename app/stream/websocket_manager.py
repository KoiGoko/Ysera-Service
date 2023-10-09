from fastapi import FastAPI, WebSocket
import uvicorn
import asyncio


class WebSocketManager:
    def __init__(self):
        self.connected_clients = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connected_clients.add(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.connected_clients.remove(websocket)

    async def send_json(self, message: str):
        await asyncio.gather(
            *[client.send_text(message) for client in self.connected_clients]
        )


app = FastAPI()
websocket_manager = WebSocketManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            # 在这里处理接收到的数据，你可以对数据进行处理后再发送
            await websocket_manager.send_json(data)
    except Exception as e:
        print(f"WebSocket Error: {e}")
    finally:
        await websocket_manager.disconnect(websocket)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
