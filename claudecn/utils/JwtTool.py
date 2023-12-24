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
    except jwt.exceptions.DecodeError as e:
        print('Invalid token: ', e)
    except jwt.exceptions.ExpiredSignatureError as e:
        print('Token has expired: ', e)
    except jwt.exceptions.InvalidAlgorithmError as e:
        print('Invalid algorithm: ', e)
    except jwt.exceptions.InvalidAudienceError as e:
        print('Invalid audience: ', e)
    except jwt.exceptions.InvalidIssuerError as e:
        print('Invalid issuer: ', e)
    except Exception as e:
        print('An unexpected error occurred: ', e)
    return ''


def obtain_jwt_token(member):
    expires = datetime.utcnow() + timedelta(days=30)
    token = jwt.encode({
        'id': member.id,
        'name': member.login_name,
        'exp': expires
    }, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)
    return token


