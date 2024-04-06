from kiteconnect import KiteConnect
from pydantic import BaseModel


class LoginUrl(BaseModel):
    login_url: str


class LoginUrlModel(BaseModel):
    kite_instance: KiteConnect = None

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, kite_instance: KiteConnect):
        super().__init__(kite_instance=kite_instance)

    def execute(self) -> 'LoginUrl':
        login_url = self.kite_instance.login_url()
        login_url = "login url"
        return LoginUrl(login_url=login_url)
