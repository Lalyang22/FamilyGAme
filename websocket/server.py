import asyncio
import websockets
import json

clients = {}
game_status = "playing"  # Track if game is still active or done

async def handle_client(websocket, path=None):
    """Handles WebSocket connections"""
    try:
        async for message in websocket:
            data = json.loads(message)

            if data["type"] == "register":
                client_id = data["clientId"]
                clients[client_id] = websocket
                print(f"✅ {client_id} registered successfully.")

            elif data["type"] == "question_selected":
                global game_status
                game_status = "playing"  # Reset game status for new question

                # Extract only text and points separately
                question_payload = {
                    "type": "question_selected",
                    "question": data["question"],
                    "answers": [answer["text"] for answer in data["answers"]],  # Extract text
                    "points": [answer["points"] for answer in data["answers"]]  # Extract points
                }

                # Send to Admin Question Viewer
                if "admin_question" in clients:
                    await clients["admin_question"].send(json.dumps({
                        "type": "question_selected",
                        "question": data["question"]
                    }))
                    print(f"📤 Sent question to admin_question: {data['question']}")

                # Send to Monitor 3
                if "monitor3" in clients:
                    await clients["monitor3"].send(json.dumps(question_payload))
                    print(f"📤 Sent question to monitor3: {data['question']}")

            elif data["type"] == "answer_selected":
                answer_text = data["answer"]
                pointsToAdd = data["pointsToAdd"]

                # If game is finished, stop counting points but still reveal the answer
                if game_status == "done":
                    pointsToAdd = 0  # Stop adding points but still flip answers

                print(f"🎯 Answer Selected: {answer_text} (Points Added: {pointsToAdd})")

                # Broadcast to Monitor 3
                if "monitor3" in clients:
                    await clients["monitor3"].send(json.dumps({
                        "type": "answer_selected",
                        "answer": answer_text,
                        "pointsToAdd": pointsToAdd  # Send 0 if game is done
                    }))

            elif data["type"] == "game_status":
                # Ensure game status is updated and winner is included
                game_status = "done"
                winner = data["winner"]
                print(f"🏆 Game finished. Winner: {winner}")
                
                # ✅ Debug: Print ALL clients before broadcasting
                print(f"📡 Sending game_status to: {list(clients.keys())}")

                # ✅ Broadcast to all clients (Ensure Monitor 3 receives)
                for client_id, ws in clients.items():
                    try:
                        message = json.dumps({
                            "type": "game_status",
                            "status": "done",
                            "winner": winner
                        })
                        await ws.send(message)
                        print(f"📤 Sent game_status to {client_id}")
                    except Exception as e:
                        print(f"⚠️ Error sending to {client_id}: {e}")

                # ✅ Ensure message is sent to Monitor 3
                if "monitor3" in clients:
                    message = json.dumps({
                        "type": "game_status",
                        "status": "done",
                        "winner": winner
                    })
                    await clients["monitor3"].send(message)
                    print(f"📤 Sent to Monitor 3: {message}")
                else:
                    print("⚠️ Monitor 3 not connected.")


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
    async with websockets.serve(handle_client, "localhost", 8080):
        await asyncio.Future()  # Keeps the server running

try:
    asyncio.run(main())
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
