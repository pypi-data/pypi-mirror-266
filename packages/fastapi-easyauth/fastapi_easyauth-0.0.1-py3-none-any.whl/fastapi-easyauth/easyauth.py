import hashlib
from fastapi import HTTPException, Request, Response
from . import exp
from .jwt import Jwt

class Auth:
    
    def __init__(self, cookie_name: str, jwt: Jwt, expires: int = exp.EXPIRES_30_DAYS):
        self.cookie_name = cookie_name
        self.jwt = jwt
        self.expires = expires
    

    def active_user(self, request: Request, response: Response):
        token = request.cookies.get(self.cookie_name)

        if not token: return False
        
        user = self.jwt.decode_token(token, full = False)
        
        response.set_cookie(
            key = self.cookie_name,
            value = token,
            expires = self.expires
            )
        
        return user

    def save_token_in_cookie(self, response: Response, token: str, expires: int = exp.EXPIRES_30_DAYS):
        response.set_cookie(
            key = self.cookie_name,
            value = token,
            expires = expires
        )

    
    def get_token(self, request: Request):
        token = request.cookies.get(self.cookie_name)
        return token
        
    
def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()


def not_authorized():
    return HTTPException(
            status_code = 401,
            detail = 'Unauthorized'
        )