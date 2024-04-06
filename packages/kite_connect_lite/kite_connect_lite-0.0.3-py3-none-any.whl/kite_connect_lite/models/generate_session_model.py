from pydantic import BaseModel
from kiteconnect import (KiteConnect, KiteTicker)


class SessionAccessToken(BaseModel):
    access_token: str


class GenerateSessionModel(BaseModel):
    request_token: str = None
    api_secret: str = None
    kite_instance: KiteConnect = None

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, kite_instance: KiteConnect):
        super().__init__(kite_instance=kite_instance)

    def set_request_token(self, request_token: str) -> 'GenerateSessionModel':
        self.request_token = request_token
        return self

    def set_api_secret(self, api_secret: str) -> 'GenerateSessionModel':
        self.api_secret = api_secret
        return self

    def execute(self) -> 'SessionAccessToken':
        access_token = self.kite_instance.generate_session(
            self.request_token, self.api_secret)["access_token"]
        access_token = "access token"
        return SessionAccessToken(
            access_token=access_token
        )
