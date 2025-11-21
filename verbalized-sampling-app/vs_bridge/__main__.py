"""
Entry point for running vs_bridge as a module
Usage: python -m vs_bridge
"""

if __name__ == "__main__":
    # Use absolute imports for PyInstaller
    import uvicorn
    import vs_bridge.main

    app = vs_bridge.main.app

    # Run FastAPI server on localhost:8765
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8765,
        log_level="info"
    )
