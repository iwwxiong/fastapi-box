from pydantic import BaseModel


class UserSchema(BaseModel):

    uid: int
    username: str
    role: str
