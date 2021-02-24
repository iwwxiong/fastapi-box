
from pydantic import BaseModel


class AuthSchema(BaseModel):
    username: str
    password: str
    # authcode: str
