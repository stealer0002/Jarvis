"""
Web routes for JARVIS
HTTP and WebSocket endpoints
"""

import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pathlib import Path
from core.agent import agent

router = APIRouter()

# Get the static files directory
STATIC_DIR = Path(__file__).parent / "static"


@router.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main HTML page."""
    html_file = STATIC_DIR / "index.html"
    return html_file.read_text(encoding="utf-8")


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    status = await agent.check_status()
    return {
        "status": "ok",
        "agent": status
    }


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat."""
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message = json.loads(data)
            
            msg_type = message.get("type", "message")
            
            if msg_type == "message":
                # Process user message
                user_text = message.get("content", "")
                if user_text:
                    try:
                        response = await agent.process_message(user_text)
                        await websocket.send_json({
                            "type": "response",
                            "content": response
                        })
                    except Exception as e:
                        await websocket.send_json({
                            "type": "error",
                            "content": str(e)
                        })
            
            elif msg_type == "clear":
                # Clear conversation history
                agent.clear_history()
                await websocket.send_json({
                    "type": "response",
                    "content": "Conversa limpa. Como posso ajudar?"
                })
            
            elif msg_type == "status":
                # Get system status
                status = await agent.check_status()
                await websocket.send_json({
                    "type": "status",
                    "content": status
                })
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
