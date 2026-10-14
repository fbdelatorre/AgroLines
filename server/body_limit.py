"""Bound HTTP import memory without logging request bodies or credentials."""

from fastapi import HTTPException
from starlette.responses import JSONResponse

LIMIT = 48 * 1024 * 1024


class BodyLimit:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        headers = dict(scope.get("headers", []))
        try:
            length = int(headers.get(b"content-length", b"0"))
        except ValueError:
            length = LIMIT + 1
        if length > LIMIT:
            return await JSONResponse({"detail": "Requisição acima de 48 MiB."}, status_code=413)(
                scope, receive, send
            )
        total = 0

        async def bounded_receive():
            nonlocal total
            message = await receive()
            total += len(message.get("body", b""))
            if total > LIMIT:
                raise HTTPException(413, "Requisição acima de 48 MiB.")
            return message

        await self.app(scope, bounded_receive, send)
