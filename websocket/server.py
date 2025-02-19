import asyncio
import websockets
import json

clients = {}

async def handle_client(websocket, path=None):  # ✅ FIX: Added default value for path
    """Handles WebSocket connections"""
    try:
        async for message in websocket:
            data = json.loads(message)

            if data["type"] == "register":
                client_id = data["clientId"]
                clients[client_id] = websocket
                print(f"✅ {client_id} registered successfully.")

            elif data["type"] == "send_message":
                monitor_id = data["monitorId"]
                if monitor_id in clients:
                    await clients[monitor_id].send(json.dumps({
                        "type": "chat_message",
                        "text": data["text"]
                    }))
                    print(f"📤 Sending message to {monitor_id}: {data['text']}")
                else:
                    print(f"⚠️ Monitor {monitor_id} not found.")

            elif data["type"] == "question_selected":
                question_payload = {
                    "type": "question_selected",
                    "question": data["question"],
                    "answers": data["answers"],
                    "points": data["points"]
                }
                for target in ["admin", "monitor3"]:
                    if target in clients:
                        await clients[target].send(json.dumps(question_payload))
                        print(f"📤 Sending question to {target}: {data['question']}")

            elif data["type"] == "answer_selected":
                answer_text = data["answer"]
                print(f"📢 Relaying answer to Monitor 3: {answer_text}")

                if "monitor3" in clients:
                    await clients["monitor3"].send(json.dumps({
                        "type": "answer_selected",
                        "answer": answer_text
                    }))

    except websockets.exceptions.ConnectionClosed:
        print(f"❌ Client disconnected.")
    finally:
        disconnected_clients = [key for key, value in clients.items() if value == websocket]
        for client in disconnected_clients:
            del clients[client]
            print(f"🔴 {client} removed from clients.")

async def main():
    """Start the WebSocket server"""
    print("🚀 WebSocket Server Started on ws://localhost:8080")

    # ✅ FIX: `path` is no longer required in websockets 11+
    async with websockets.serve(handle_client, "localhost", 8080):
        await asyncio.Future()  # Keeps the server running

# ✅ FIX: Ensure asyncio runs properly
try:
    asyncio.run(main())
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
