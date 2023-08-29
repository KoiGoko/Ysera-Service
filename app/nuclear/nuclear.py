from pydantic import BaseModel


class Nuclear(BaseModel):
    id: int
    username: str
    email: str
