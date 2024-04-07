from uvicorn import run
import chainlo.agenta_cli.agenta as agenta
import _app  # This will register the routes with the FastAPI application
import os

try:
    import ingest
except ImportError:
    pass


if __name__ == "__main__":
    run("agenta:app", host="0.0.0.0", port=80)
