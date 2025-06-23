from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Hasher:
    @staticmethod
    def verify(plain_token: str, token_hash: str) -> bool:
        return pwd_context.verify(plain_token, token_hash)

    @staticmethod
    def hash(token: str) -> str:
        return pwd_context.hash(token)