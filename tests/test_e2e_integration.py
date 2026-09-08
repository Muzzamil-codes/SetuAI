import asyncio
import httpx
import websockets
import json

async def run_test():
    async with httpx.AsyncClient() as client:
        # 1. Create a task
        print("Creating task...")
        resp = await client.post("http://localhost:8000/task", json={
            "modality": "image",
            "content": "uploads/scan_001.jpg",
            "context": {}
        })
        resp.raise_for_status()
        task_id = resp.json()["task_id"]
        print(f"Task created: {task_id}")
        
        # 2. Connect to websocket to stream trace events
        print("Connecting to websocket...")
        uri = f"ws://localhost:8000/trace/{task_id}"
        try:
            async with websockets.connect(uri) as websocket:
                print("Listening for events...")
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    step = data.get("step")
                    payload = data.get("payload", {})
                    print(f"[{step}] {payload}")
                    
                    if step in ["done", "error"]:
                        break
        except Exception as e:
            print(f"Websocket error: {e}")

if __name__ == "__main__":
    asyncio.run(run_test())
