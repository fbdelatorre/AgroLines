from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from server.auth import router as auth_router
from server.config import get_settings
from server.properties import router as properties_router


def create_app(settings=None, engine=None) -> FastAPI:
    settings = settings or get_settings()
    app = FastAPI(title=settings.app_name)
    app.state.settings = settings
    app.state.engine = engine
    app.include_router(auth_router)
    app.include_router(properties_router)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        return JSONResponse(
            status_code=422,
            content={
                "detail": [
                    {"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]}
                    for e in exc.errors()
                ]
            },
        )

    @app.get("/health", tags=["saúde"])
    def health() -> dict[str, str]:
        # Liveness only: does not claim database readiness or synchronization.
        return {"status": "ok", "service": "agrolines", "version": "0.1.0"}

    return app


app = create_app()
