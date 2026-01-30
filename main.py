"""
JARVIS - Autonomous AI Desktop Agent
Main entry point
"""

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from contextlib import asynccontextmanager

import config
from web.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):

    """Lifespan context manager for startup and shutdown events."""
    # Startup
    print(f"""
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║       ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗        ║
║       ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝        ║
║       ██║███████║██████╔╝██║   ██║██║███████╗        ║
║  ██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║        ║
║  ╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║        ║
║   ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝        ║
║                                                       ║
║           Autonomous AI Desktop Agent                 ║
║                                                       ║
╠═══════════════════════════════════════════════════════╣
║                                                       ║
║   🖥️  Local:   http://localhost:{config.PORT:<5}                ║
║   📱  Network: http://0.0.0.0:{config.PORT:<5}                  ║
║   🤖  Model:   {config.OLLAMA_MODEL:<26}          ║
║                                                       ║
║   Para acessar do celular, use o IP do seu PC        ║
║   Execute: ipconfig | findstr IPv4                   ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
    """)
    
    yield  # Application runs here
    
    # Shutdown
    from core.agent import agent
    await agent.close()
    print("\n👋 JARVIS desligado. Até a próxima!")


# Create FastAPI app with lifespan
app = FastAPI(
    title="JARVIS",
    description="Autonomous AI Desktop Agent",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for mobile access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = Path(__file__).parent / "web" / "static"
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Mount screenshots folder
screenshots_path = Path(__file__).parent / "screenshots"
screenshots_path.mkdir(exist_ok=True)
app.mount("/screenshots", StaticFiles(directory=screenshots_path), name="screenshots")

# Include routes
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=False,
        log_level="info"
    )
