from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse
from jose import JWTError, jwt
from utils.auth import SECRET_KEY, ALGORITHM
import os

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.url.path in ["/login/", "/register/", "/token", "/static/css/styles.css"]:
            response = await call_next(request)
            return response

        try:
            token = request.cookies.get("access_token")
            if token:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                request.state.user = payload.get("sub")
            else:
                request.state.user = None
        except JWTError:
            request.state.user = None

        if not request.state.user:
            return RedirectResponse(url="/login/")
        
        response = await call_next(request)
        return response
