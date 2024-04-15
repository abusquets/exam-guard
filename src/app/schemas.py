from pydantic import BaseModel


class Session(BaseModel):
    uuid: str
    expires: int
    username: str


class DetailResponse(BaseModel):
    detail: str
