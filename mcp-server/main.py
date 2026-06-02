import logging
import os
import time
import inspect
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=False)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    from src.server import mcp
    from src.database.connection import check_connection

    logger.info("Starting MCP Server...")
    max_wait_seconds = int(os.getenv("DB_CONNECT_TIMEOUT_SECONDS", "120"))
    deadline = time.time() + max_wait_seconds

    while True:
        if check_connection():
            host = os.getenv("MCP_HTTP_HOST", "0.0.0.0")
            port = int(os.getenv("MCP_HTTP_PORT", "8000"))
            logger.info(f"Starting MCP HTTP transport on {host}:{port}")
            run_params = inspect.signature(mcp.run).parameters
            if "transport" not in run_params:
                mcp.run()
                exit(0)

            last_error: Exception | None = None
            for transport in ("streamable-http", "http"):
                try:
                    mcp.run(transport=transport)
                    exit(0)
                except ValueError as e:
                    last_error = e

            raise last_error or RuntimeError("Failed to start MCP server transport")
            exit(0)

        if time.time() >= deadline:
            logger.error("Could not start server: Database connection failed.")
            exit(1)

        time.sleep(2)
