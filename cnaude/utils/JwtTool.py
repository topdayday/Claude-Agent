import string,secrets,jwt
from django.conf import settings
from datetime import datetime, timedelta


def generate_api_token(length=32):
    alphabet = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(alphabet) for i in range(length))
    return token


def protected_view(token):
    try:
        decoded_token = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return decoded_token
    except BaseException as e:
        print('protected_view error: ', e)
    return ''


def obtain_jwt_token(member):
    expires = datetime.utcnow() + timedelta(days=30)
    token = jwt.encode({
        'id': member.id,
        'name': member.login_name,
        'exp': expires
    }, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)
    return token


