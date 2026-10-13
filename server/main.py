from fastapi import FastAPI

from server.config import get_settings


def create_app() -> FastAPI:
    app = FastAPI(title=get_settings().app_name)

    @app.get("/health", tags=["saúde"])
    def health() -> dict[str, str]:
        # Liveness only: does not claim database readiness or synchronization.
        return {"status": "ok", "service": "agrolines", "version": "0.1.0"}

    return app


app = create_app()
