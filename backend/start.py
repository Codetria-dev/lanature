#!/usr/bin/env python3
"""
Start script for Railway deployment.
Uses PORT environment variable or defaults to 8000.
"""
import os
import uvicorn

if __name__ == "__main__":
    # Railway provides PORT environment variable
    # Default to 8000 if not set (for local development)
    port_env = os.environ.get("PORT", "8000")
    port = int(port_env)
    
    print(f"Starting server on port {port} (PORT env: {port_env})")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
