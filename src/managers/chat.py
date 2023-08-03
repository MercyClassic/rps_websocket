from starlette.websockets import WebSocket, WebSocketDisconnect


class ChatConnectionManager:
    def __init__(self):
        self.connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket, client_id: int):
        await websocket.accept()
        self.connections.append(websocket)
        try:
            while True:
                data = await websocket.receive_text()
                await manager.broadcast(f'Client #{client_id} says: {data}')
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            await manager.broadcast(f'Client #{client_id} left the chat')

    def disconnect(self, websocket: WebSocket):
        self.connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.connections:
            await connection.send_text(message)


manager = ChatConnectionManager()
