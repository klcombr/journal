"""journal-server: FastAPI app with auth, entry CRUD and WebSocket realtime."""

from .app import app

__all__ = ["app"]
__version__ = "2.0.0"
