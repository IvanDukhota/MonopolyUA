import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import UntypedToken
from channels.db import database_sync_to_async

User = get_user_model()

@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return None

class JwtAuthMiddleware:

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        qs = scope.get("query_string", b"").decode()
        token = next((p.split("=",1)[1] for p in qs.split("&") if p.startswith("token=")), None)

        if token:
            try:
                UntypedToken(token)
                signing_key = settings.SIMPLE_JWT.get("SIGNING_KEY") or settings.SECRET_KEY
                algorithm   = settings.SIMPLE_JWT.get("ALGORITHM", "HS256")
                payload = jwt.decode(token, signing_key, algorithms=[algorithm])

                # user = await get_user(payload.get("user_id"))
                user = payload.get("user_id")
                if user:
                    scope["user_id"] = user
            except (TokenError, InvalidToken, jwt.DecodeError):
                pass

        return await self.app(scope, receive, send)
