from contextvars import ContextVar, Token
from typing import Optional, Union

from sqlalchemy.orm import Session

_session: ContextVar[Optional[Session]] = ContextVar("_session", default=None)


def get_session() -> Session:
    """
    Get the current session.

    :raises RuntimeError: If no session is available.
    :return: The current session.
    """
    session = _session.get()
    if session is None:
        raise RuntimeError("No session available")
    return session


def set_session(session: Session) -> Token[Union[Session, None]]:
    """
    Set the current session.

    :param session: The session to set.
    :return: A token that can be used to reset the session.
    """
    return _session.set(session)


def reset_session(token: Token[Union[Session, None]]) -> None:
    """
    Reset the current session.

    :param token: The token to reset the session.
    """
    _session.reset(token)
