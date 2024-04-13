from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas import Session


http_bearer = HTTPBearer()


async def check_access_token(_: HTTPAuthorizationCredentials = Depends(http_bearer)) -> Session:
    # TODO: Implement token validation
    # For now, just return a fake session
    return Session(uuid='123', expires=60 * 5, username='fake-user')
