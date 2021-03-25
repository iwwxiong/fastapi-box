import uuid
import logging
from sqlalchemy.orm import Session

from models.antapt import Users
from utils.common_func import compute_md5

logger = logging.getLogger("webapi")


def generate_salt_and_password(password: str) -> (str, str):
    salt = uuid.uuid4().hex
    hash_password = compute_md5(password, salt=salt)
    return salt, hash_password


def create_user(dbsession: Session, username: str, password: str, role: str) -> (bool, Users):
    user = dbsession.query(Users).filter_by(username=username).first()
    if user is not None:
        return False, user

    salt, hash_password = generate_salt_and_password(password)
    user = Users(
        username=username,
        password=hash_password,
        salt=salt,
        role=role
    )
    dbsession.add(user)
    try:
        dbsession.commit()
    except Exception as e:  # noqa
        dbsession.rollback()
        logger.exception("create_user failure")
        return False, None

    return True, user
