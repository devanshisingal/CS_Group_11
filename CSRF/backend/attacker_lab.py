from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from backend.config import FRONTEND_DIR


app = FastAPI(title="SecureBank CSRF Threat Model")


@app.get("/", include_in_schema=False)
def threat_model_page() -> FileResponse:
    return FileResponse(Path(FRONTEND_DIR) / "attacker.html")
