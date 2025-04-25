import jwt
from django.conf import settings
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

class CustomUser:
    def __init__(self, user_id, name, email):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.is_authenticated = True

class CustomTokenAuthentication(authentication.BaseAuthentication):
    keyword = 'Bearer'

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,  # Use the same secret as token generator
                algorithms=['HS256']
            )
            user_id = payload.get('uid')

            if not user_id:
                raise AuthenticationFailed('Invalid token: uid missing')
            
            user = CustomUser(
                user_id=user_id,
                name=payload.get('name'), 
                email=payload.get('email')
            )
            return (user, token)
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.DecodeError:
            raise AuthenticationFailed('Error decoding token')