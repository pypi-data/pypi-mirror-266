import os
from kiteconnect import (KiteConnect, KiteTicker)

from models.place_normal_order_model import PlaceNormalOrderModel
from models.generate_session_model import GenerateSessionModel
from models.login_url_model import LoginUrlModel


class KiteConnectLite:
    def __init__(self, api_key: str):
        self.kite_api_key: str = api_key
        self.kite_instance = KiteConnect(api_key=self.kite_api_key)

    def login_url(self) -> 'LoginUrlModel':
        return LoginUrlModel(self.kite_instance)

    def generate_session(self) -> 'GenerateSessionModel':
        return GenerateSessionModel(self.kite_instance)

    def place_normal_order(self) -> 'PlaceNormalOrderModel':
        return PlaceNormalOrderModel(self.kite_instance)
