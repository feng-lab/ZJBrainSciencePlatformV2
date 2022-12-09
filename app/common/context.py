from fastapi import Depends
from sqlalchemy.orm import Session

from app.common.user_auth import AccessLevel, oauth2_scheme, verify_current_user
from app.db.database import get_db_session


class Context:
    def __init__(self, db: Session, token: str, api_access_level: int | None):
        self.db = db
        self.user_id = verify_current_user(db, token, api_access_level)


def all_user_context(
    db: Session = Depends(get_db_session), token: str = Depends(oauth2_scheme)
) -> Context:
    return Context(db, token, api_access_level=None)


def human_subject_context(
    db: Session = Depends(get_db_session), token: str = Depends(oauth2_scheme)
) -> Context:
    # noinspection PyTypeChecker
    return Context(db, token, api_access_level=AccessLevel.HUMAN_SUBJECT.value)


def researcher_context(
    db: Session = Depends(get_db_session), token: str = Depends(oauth2_scheme)
) -> Context:
    # noinspection PyTypeChecker
    return Context(db, token, api_access_level=AccessLevel.RESEARCHER.value)


def administrator_context(
    db: Session = Depends(get_db_session), token: str = Depends(oauth2_scheme)
) -> Context:
    # noinspection PyTypeChecker
    return Context(db, token, api_access_level=AccessLevel.ADMINISTRATOR.value)
