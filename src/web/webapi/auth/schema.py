import re
from pydantic import BaseModel, constr, validator

password_regex = r"^[\w]{5,32}$"


class AuthSchema(BaseModel):
    username: constr(min_length=4, max_length=32)
    password: str

    @validator("password")
    def password_validator(cls, value):
        if not re.match(password_regex, value):
            raise ValueError("密码格式不符合要求")
        return value
