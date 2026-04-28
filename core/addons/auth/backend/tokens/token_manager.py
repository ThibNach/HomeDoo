import datetime
import jwt

from core.backend import config


class TokenManager:
    def __init__(self, secret, algorithm="HS256", expiration_hours=24):
        self.secret = secret
        self.algorithm = algorithm
        self.expiration_hours = expiration_hours

    def generate(self, payload_data):
        payload = {
            **payload_data,
            "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=self.expiration_hours)
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def verify(self, token):
        try:
            return jwt.decode(token, self.secret, algorithms=[self.algorithm])
        except jwt.PyJWTError:
            return None

token_manager = TokenManager(config.JWT_SECRET)