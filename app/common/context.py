from fastapi import Depends
from redis import Redis
from sqlalchemy.orm import Session

from app.common.user_auth import AccessLevel, oauth2_scheme, verify_current_user
from app.db import get_db_session
from app.db.cache import get_redis


class Context:
    def __init__(self, db: Session, token: str | None, api_access_level: int | None):
        self.db: Session = db
        self.cache: Redis = get_redis()
        if token is None or api_access_level is None:
            self.user_id: int | None = None
        else:
            self.user_id: int | None = verify_current_user(db, self.cache, token, api_access_level)


def not_logon_context(db: Session = Depends(get_db_session)) -> Context:
    return Context(db, None, None)


def all_user_context(
    db: Session = Depends(get_db_session), token: str = Depends(oauth2_scheme)
) -> Context:
    return Context(db, token, AccessLevel.MINIMUM.value)


def human_subject_context(
    db: Session = Depends(get_db_session), token: str = Depends(oauth2_scheme)
) -> Context:
    return Context(db, token, AccessLevel.HUMAN_SUBJECT.value)


def researcher_context(
    db: Session = Depends(get_db_session), token: str = Depends(oauth2_scheme)
) -> Context:
    return Context(db, token, AccessLevel.RESEARCHER.value)


def administrator_context(
    db: Session = Depends(get_db_session), token: str = Depends(oauth2_scheme)
) -> Context:
    return Context(db, token, AccessLevel.ADMINISTRATOR.value)
