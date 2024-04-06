from contextlib import contextmanager
from typing import Any, Dict, Iterator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .session import get_session, reset_session, set_session


class DatabaseManager:
    """
    A class that manages the database connection and provides session management.

    :param db_url: The URL of the database.
    :param engine_args: Optional arguments to be passed to the database engine.
    :param session_args: Optional arguments to be passed to the session factory.
    """

    def __init__(
        self,
        db_url: str,
        engine_args: Optional[Dict[str, Any]] = None,
        session_args: Optional[Dict[str, Any]] = None,
    ) -> None:
        db_url = db_url
        engine_args = engine_args or {}
        session_args = session_args or {}

        self.engine = create_engine(db_url, **engine_args)
        self.session_factory: sessionmaker[Session] = sessionmaker(bind=self.engine, **session_args)

    @property
    def session(self) -> Session:
        """
        A property that provides a session object.

        :return: A SQLAlchemy session object.
        """
        return get_session()

    @contextmanager
    def session_ctx(self) -> Iterator[Session]:
        """
        Context manager for providing a session object.

        :yield: A SQLAlchemy session object.
        """
        session = self.session_factory()
        token = set_session(session)
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
            reset_session(token)
