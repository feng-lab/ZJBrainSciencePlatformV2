from fastapi import Depends
from redis import Redis
from sqlalchemy.orm import Session

from app.common.exception import ServiceError
from app.common.user_auth import AccessLevel, oauth2_scheme, verify_current_user
from app.db import get_db_session
from app.db.cache import get_redis


class Context:
    def __init__(self, db: Session, token: str | None, api_access_level: int | None):
        self.db: Session = db
        self.cache: Redis = get_redis()
        if token is None and api_access_level is None:
            self.user_id: int | None = None
        elif token is None:
            raise ServiceError.not_login()
        else:
            self.user_id: int | None = verify_current_user(db, self.cache, token, api_access_level)


class NotLogonContext(Context):
    def __init__(self, db: Session = Depends(get_db_session)):
        super().__init__(db, None, None)


class AllUserContext(Context):
    def __init__(self, db: Session = Depends(get_db_session), token: str = Depends(oauth2_scheme)):
        super().__init__(db, token, AccessLevel.MINIMUM)


class HumanSubjectContext(Context):
    def __init__(self, db: Session = Depends(get_db_session), token: str = Depends(oauth2_scheme)):
        super().__init__(db, token, AccessLevel.HUMAN_SUBJECT)


class ResearcherContext(Context):
    def __init__(self, db: Session = Depends(get_db_session), token: str = Depends(oauth2_scheme)):
        super().__init__(db, token, AccessLevel.RESEARCHER)


class AdministratorContext(Context):
    def __init__(self, db: Session = Depends(get_db_session), token: str = Depends(oauth2_scheme)):
        super().__init__(db, token, AccessLevel.ADMINISTRATOR)
