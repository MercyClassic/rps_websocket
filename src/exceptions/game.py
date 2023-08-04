from starlette.websockets import WebSocket


async def not_found(websocket: WebSocket):
    await websocket.send_json({'action': 'error', 'detail': 'Not found'})


async def cant_connect_to_own_game(websocket: WebSocket):
    await websocket.send_json({'action': 'error', 'detail': 'You cant connect to own game'})


async def cant_connect_to_closed_game(websocket: WebSocket):
    await websocket.send_json({'action': 'error', 'detail': 'You cant connect to closed game'})


async def cant_change_state_now(websocket: WebSocket):
    await websocket.send_json({'action': 'error', 'detail': 'You cant change state now'})


async def unavailable_state(websocket: WebSocket):
    await websocket.send_json({'action': 'error', 'detail': 'Unavailable state'})
