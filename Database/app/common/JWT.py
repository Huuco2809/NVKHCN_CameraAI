"""
aioz.truongle - Mar 29, 2023
"""
import logging
from jose import jwt
from datetime import datetime
from app.common import errors as app_errors
from app.common._app import SECRET_KEY, EXPIRES

logger = logging.getLogger("app.common.jwt")

ALGORITHM = "HS256"


def create_token(data: dict) -> str:
    to_encode = data.copy()

    # expire time of the token
    expire = datetime.utcnow() + EXPIRES
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # return the generated token
    return encoded_jwt


def check_token(token: str) -> [dict, bool]:
    try:
        # try to decode the token, it will
        # raise error if the token is not correct
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload, True

    except jwt.ExpiredSignatureError as e:
        logger.error(f"Authorization failed: {e}")
        raise app_errors.AuthorizationFailed(message='Authorization token has expired')

    except jwt.JWTClaimsError as e:
        logger.error(f"Authorization failed: {e}")
        raise app_errors.AuthorizationFailed(message='Incorrect claims, check the audience and issuer.')

    except jwt.JWTError as e:
        logger.error(f"Authorization failed: {e}")
        raise app_errors.AuthorizationFailed(message='Unable to decode authorization token headers')

    except Exception as e:
        logger.error(f"Authorization failed: {e}")
        raise app_errors.AuthorizationFailed(message='Unable to parse authentication token')


if __name__ == '__main__':
    import asyncio

    _payload = {"test": "test"}
    # tk = asyncio.run(create_token(payload))
    tk = create_token(_payload)
    print(tk)
