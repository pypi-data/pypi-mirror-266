from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from ...manager import DatabaseManager
from ...session import reset_session, set_session


class SQLAlchemyMiddleware(BaseHTTPMiddleware):
    """
    Middleware class for integrating SQLAlchemy with FastAPI.

    This middleware manages the database session for each request by creating a new session
    and closing it after the request is processed.

    :param app: The ASGI application.
    :param db: The DatabaseManager instance.
    """

    def __init__(self, app: ASGIApp, db: DatabaseManager) -> None:
        super().__init__(app)
        self.db = db

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        Dispatch method that handles the request and response.

        This method creates a new database session using the session context manager provided
        by the DatabaseManager instance. It then calls the next middleware or the application
        itself to handle the request. After the response is received, the session is closed.

        :param request: The incoming request.
        :param call_next: The next middleware or application to call.
        :return: The response.
        """

        response = Response("Internal server error", status_code=500)
        try:
            session = self.db.session_factory()
            token = set_session(session)
            response = await call_next(request)
        finally:
            session.close()
            reset_session(token)
        return response
