from fastapi.security import HTTPAuthorizationCredentials, http
from fastapi import Depends, HTTPException, status, Request
from tools._shared._model import BaseUser
import sentry_sdk
UNAUTHORISED_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid authentication credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
def authenticate(req : Request) -> dict | None:
    try:
        logged_in_user = BaseUser.logged_in_user(req.cookies)
        req.state.user = logged_in_user
        if logged_in_user:
            sentry_sdk.set_user(logged_in_user)
            return logged_in_user
        else:
            sentry_sdk.set_user(None)
            raise UNAUTHORISED_EXCEPTION
    except Exception as e:
        raise UNAUTHORISED_EXCEPTION
def tool_tagger(name):
    def tag():
        sentry_sdk.set_tag("tool", name)
    return tag