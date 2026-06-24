import asyncio
import json
import os
import signal
import sys
import websockets
from ai_brain import AIBrain
from computer import ComputerController
from memory import Memory
from screen import ScreenAnalyzer
from speech import SpeechRecognizer
from startup import run_checks

if not run_checks():
    print("[STARTUP] Exiting due to failed checks")
    sys.exit(1)

brain = AIBrain()
computer = ComputerController()
memory = Memory()
screen = ScreenAnalyzer()
speech = SpeechRecognizer()

connected_clients = set()
background_tasks = {}

PID_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend.pid")

def write_pid():
    try:
        with open(PID_PATH, "w") as f:
            f.write(str(os.getpid()))
    except Exception:
        pass

def remove_pid():
    try:
        if os.path.exists(PID_PATH):
            os.remove(PID_PATH)
    except Exception:
        pass

async def notify_user(message, msg_type="response"):
    for ws in connected_clients:
        try:
            await ws.send(json.dumps({
                "type": msg_type,
                "message": message,
                "background": True
            }))
        except Exception:
            pass

async def handle_client(websocket):
    connected_clients.add(websocket)
    print(f"[CONNECT] Client connected. Total: {len(connected_clients)}")
    try:
        await websocket.send(json.dumps({"type": "status", "message": "Jarvis is ready"}))
        async for message in websocket:
            print(f"[RECEIVED] {message[:200]}")
            data = json.loads(message)
            await process_message(websocket, data)
    except websockets.exceptions.ConnectionClosed as e:
        print(f"[DISCONNECT] {e}")
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
    finally:
        connected_clients.discard(websocket)
        print(f"[DISCONNECT] Client removed. Total: {len(connected_clients)}")

async def process_message(websocket, data):
    msg_type = data.get("type")
    if msg_type not in ("chat", "history_request", "clear_history", "audio_transcribe"):
        return

    if msg_type == "audio_transcribe":
        audio_data = data.get("audio", "")
        format = data.get("format", "webm")
        if not audio_data:
            await websocket.send(json.dumps({"type": "error", "message": "No audio data"}))
            return
        result = speech.transcribe(audio_data, format)
        await websocket.send(json.dumps({"type": "transcription", "text": result.get("text", ""), "success": result.get("success", False)}))
        return

    if msg_type == "history_request":
        limit = min(data.get("limit", 50), 200)
        history = memory.get_recent_conversations(limit)
        await websocket.send(json.dumps({"type": "history", "messages": history}))
        return

    if msg_type == "clear_history":
        memory.clear_conversations()
        await websocket.send(json.dumps({"type": "response", "message": "Chat history cleared."}))
        return

    content = data.get("content", "")
    if not content or not isinstance(content, str):
        return

    content = content[:10000]
    use_stream = data.get("stream", True)
    print(f"[AI] User: {content[:200]}")

    if use_stream:
        await process_message_stream(websocket, content)
    else:
        await process_message_sync(websocket, content)

async def process_message_sync(websocket, content):
    try:
        response = brain.chat(content, memory)
    except Exception as e:
        print(f"[AI] Brain error: {e}")
        await websocket.send(json.dumps({"type": "error", "message": f"AI error: {str(e)}"}))
        return

    print(f"[AI] Response type: {response.get('type')}")

    if response["type"] == "chat":
        msg = response.get("message", "") or "I'm not sure how to help. Could you rephrase?"
        await websocket.send(json.dumps({"type": "response", "message": msg}))
        memory.save_conversation(content, msg)

    elif response["type"] == "error":
        await websocket.send(json.dumps({"type": "error", "message": response.get("message", "Unknown error")}))

    elif response["type"] == "action":
        action = response["action"]
        is_long = is_long_task(action)

        if is_long:
            asyncio.create_task(run_background_task(action, content))
            await websocket.send(json.dumps({
                "type": "response",
                "message": "Working on it... I'll notify you when done. You can continue using your computer."
            }))
        else:
            await run_foreground_task(websocket, action, content)

async def process_message_stream(websocket, content):
    msg_id = str(id(content))
    await websocket.send(json.dumps({"type": "stream_start", "id": msg_id}))

    try:
        for chunk in brain.chat_stream(content, memory):
            if chunk["type"] == "chunk":
                await websocket.send(json.dumps({"type": "stream_chunk", "id": msg_id, "delta": chunk["content"]}))
            elif chunk["type"] == "done":
                result = chunk["result"]
                print(f"[AI] Stream done, type: {result.get('type')}")

                if result["type"] == "chat":
                    msg = result.get("message", "") or "I'm not sure how to help. Could you rephrase?"
                    await websocket.send(json.dumps({"type": "stream_end", "id": msg_id, "message": msg}))
                    memory.save_conversation(content, msg)

                elif result["type"] == "error":
                    await websocket.send(json.dumps({"type": "stream_end", "id": msg_id, "error": result.get("message", "Unknown error")}))

                elif result["type"] == "action":
                    action = result["action"]
                    is_long = is_long_task(action)

                    if is_long:
                        asyncio.create_task(run_background_task(action, content))
                        await websocket.send(json.dumps({"type": "stream_end", "id": msg_id, "message": "Working on it... I'll notify you when done."}))
                    else:
                        await websocket.send(json.dumps({"type": "stream_end", "id": msg_id, "action": action}))

            elif chunk["type"] == "error":
                await websocket.send(json.dumps({"type": "stream_end", "id": msg_id, "error": chunk["message"]}))
                return

    except Exception as e:
        print(f"[AI] Stream error: {e}")
        await websocket.send(json.dumps({"type": "stream_end", "id": msg_id, "error": str(e)}))

def is_long_task(action):
    action_type = action.get("action", "")
    if action_type == "search_and_read":
        return True
    if action_type == "chain":
        return any(s.get("action") == "search_and_read" for s in action.get("steps", []))
    return False

async def run_foreground_task(websocket, action, content):
    try:
        result = await execute_action(action)
    except Exception as e:
        result = {"success": False, "error": str(e)}

    await websocket.send(json.dumps({
        "type": "action_result",
        "action": action,
        "result": result
    }))
    memory.save_conversation(content, f"Executed: {action.get('action')}")

async def run_background_task(action, content):
    task_id = str(id(action))
    background_tasks[task_id] = True
    print(f"[BG] Started task {task_id}")

    try:
        result = await execute_action(action)
        summary = extract_summary(result)
        await notify_user(summary)
        memory.save_conversation(content, summary)
        print(f"[BG] Task {task_id} done")
    except Exception as e:
        await notify_user(f"Task failed: {str(e)}", "error")
        print(f"[BG] Task {task_id} error: {e}")
    finally:
        background_tasks.pop(task_id, None)

async def execute_action(action):
    action_type = action.get("action", "")

    if action_type == "chain":
        return await execute_chain(action.get("steps", []))
    elif action_type == "search_and_read":
        return await execute_search_and_respond(action)
    else:
        return handle_smart_action_sync(action)

async def execute_search_and_respond(action):
    query = action.get("query", "")

    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(screen.search_and_read, query),
            timeout=90
        )
    except Exception as e:
        return {"success": False, "error": str(e)}

    if not result.get("success") or not result.get("analysis"):
        return {"success": False, "error": result.get("error", "Search failed")}

    search_text = result["analysis"]
    print(f"[SEARCH] Got {len(search_text)} chars, processing with AI...")

    brain.conversation_history.clear()

    try:
        followup = await asyncio.wait_for(
            asyncio.to_thread(
                brain.chat,
                f"I searched for you. Here are the REAL results:\n\nSearch query: {query}\nResults:\n{search_text}\n\nNow complete the user's original request using this REAL data. Do NOT make up information. Respond with the answer directly.",
                None
            ),
            timeout=30
        )

        if followup.get("type") == "chat":
            return {"success": True, "message": followup["message"]}
        else:
            return {"success": True, "message": search_text}

    except Exception as e:
        print(f"[SEARCH] Follow-up error: {e}")
        return {"success": True, "message": f"Here's what I found:\n\n{search_text}"}

async def execute_chain(steps):
    results = []
    total = len(steps)

    for i, step in enumerate(steps):
        name = step.get("action", "unknown")
        num = i + 1
        print(f"[CHAIN] Step {num}/{total}: {name}")

        try:
            if name == "wait":
                secs = min(step.get("seconds", 1), 10)
                await asyncio.wait_for(asyncio.sleep(secs), timeout=15)
                results.append({"step": num, "action": name, "result": {"success": True, "message": f"Waited {secs}s"}})
            elif name in ["screenshot", "describe_screen", "find_element", "search_and_read"]:
                result = await asyncio.wait_for(
                    asyncio.to_thread(handle_smart_action_sync, step),
                    timeout=90
                )
                results.append({"step": num, "action": name, "result": result})
            else:
                result = await asyncio.wait_for(
                    asyncio.to_thread(handle_smart_action_sync, step),
                    timeout=15
                )
                results.append({"step": num, "action": name, "result": result})

            ok = results[-1].get("result", {}).get("success", False)
            print(f"[CHAIN] Step {num}: {'OK' if ok else 'FAIL'}")

        except asyncio.TimeoutError:
            results.append({"step": num, "action": name, "result": {"success": False, "error": "Timed out"}})
        except Exception as e:
            results.append({"step": num, "action": name, "result": {"success": False, "error": str(e)}})

        await asyncio.sleep(0.3)

    completed = sum(1 for r in results if r.get("result", {}).get("success", False))
    return {"success": completed > 0, "message": f"Completed {completed}/{total} steps", "results": results}

def handle_smart_action_sync(action):
    action_type = action.get("action", "")

    if action_type == "screenshot":
        return screen.analyze_screen(action.get("question", "What is on the screen?"))
    elif action_type == "search_and_read":
        return screen.search_and_read(action.get("query", ""), action.get("read_question"))
    elif action_type == "describe_screen":
        return screen.describe_screen()
    elif action_type == "find_element":
        return screen.find_element(action.get("element", ""))
    elif action_type == "remember":
        memory.remember_fact(action.get("key", ""), action.get("value", ""))
        return {"success": True, "message": f"Remembered: {action.get('key')} = {action.get('value')}"}
    elif action_type == "recall":
        facts = memory.search_facts(action.get("query", ""))
        return {"success": True, "facts": facts} if facts else {"success": True, "message": "No matching facts found"}
    elif action_type == "remind":
        reminder = memory.add_reminder(action.get("message", ""), action.get("time", ""))
        return {"success": True, "message": f"Reminder set: {action.get('message')} at {action.get('time')}"}
    elif action_type == "list_reminders":
        pending = [r for r in memory.get_all_reminders() if not r["completed"]]
        return {"success": True, "reminders": pending}
    else:
        return computer.execute(action)

def extract_summary(result):
    if result.get("message"):
        return result["message"]
    elif result.get("analysis"):
        return result["analysis"]
    elif result.get("success"):
        return "Task completed successfully"
    else:
        return f"Task completed with issues: {result.get('error', 'unknown')}"

async def check_reminders():
    while True:
        await asyncio.sleep(30)
        pending = memory.get_pending_reminders()
        for reminder in pending:
            await notify_user(f"Reminder: {reminder['message']}", "reminder")
            memory.complete_reminder(reminder["id"])

async def main():
    host = "localhost"
    port = int(os.getenv("WS_PORT", 8765))

    write_pid()

    def shutdown_handler(sig, frame):
        print("\n[SERVER] Shutting down...")
        remove_pid()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    print(f"========================================")
    print(f"  Jarvis Backend")
    print(f"  ws://{host}:{port}")
    print(f"  Model: {brain.model}")
    print(f"  Vision: ON | Memory: ON | Reminders: ON")
    print(f"========================================")

    asyncio.create_task(check_reminders())

    async with websockets.serve(handle_client, host, port, max_size=10240):
        print(f"[SERVER] Listening")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
