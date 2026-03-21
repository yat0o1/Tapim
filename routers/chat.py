from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import or_, and_
from sqlalchemy import select, insert, update, func
from database import async_engine
from models import messages

router = APIRouter(prefix="/chat", tags=["chat"])

# Store active connections in memory
active_connections: dict[int, WebSocket] = {}  # {user_id: websocket}


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    active_connections[user_id] = websocket
    try:
        while True:
            data = await websocket.receive_json()
            receiver_id = data["receiver_id"]
            content = data["content"]

            # Save message to DB
            async with async_engine.connect() as conn:
                await conn.execute(
                    insert(messages).values(
                        sender_id=user_id,
                        receiver_id=receiver_id,
                        content=content
                    )
                )
                await conn.commit()

            # Send to receiver if online
            if receiver_id in active_connections:
                await active_connections[receiver_id].send_json({
                    "sender_id": user_id,
                    "content": content
                })

    except WebSocketDisconnect:
        active_connections.pop(user_id, None)


# Get chat history between two users
@router.get("/history/{user_id}/{other_user_id}")
async def get_chat_history(user_id: int, other_user_id: int):
    async with async_engine.connect() as conn:
        result = await conn.execute(
            select(messages)
            .where(
                or_(
                    and_(messages.c.sender_id == user_id, messages.c.receiver_id == other_user_id),
                    and_(messages.c.sender_id == other_user_id, messages.c.receiver_id == user_id)
                )
            )
            .order_by(messages.c.created_at.asc())
        )
        return result.mappings().all()


# Mark messages as read
@router.put("/read/{sender_id}/{receiver_id}")
async def mark_as_read(sender_id: int, receiver_id: int):
    async with async_engine.connect() as conn:
        await conn.execute(
            update(messages)
            .where(
                messages.c.sender_id == sender_id,
                messages.c.receiver_id == receiver_id,
                messages.c.is_read == False
            )
            .values(is_read=True)
        )
        await conn.commit()
    return {"message": "Messages marked as read"}


# Get unread messages count
@router.get("/unread/{user_id}")
async def get_unread_count(user_id: int):
    async with async_engine.connect() as conn:
        result = await conn.execute(
            select(func.count())
            .where(
                messages.c.receiver_id == user_id,
                messages.c.is_read == False
            )
        )
        count = result.scalar()
    return {"unread_count": count}