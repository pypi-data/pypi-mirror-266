from kiteconnect import KiteConnect
from pydantic import BaseModel


class PlaceNormalOrder(BaseModel):
    order_id: str


class PlaceNormalOrderModel(BaseModel):
    kite_instance: KiteConnect
    stock_name: str
    quantity: int
    order_type: str

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, kite_instance: KiteConnect):
        super().__init__(kite_instance=kite_instance)

    def set_stock_name(self, stock_name: str) -> 'PlaceNormalOrderModel':
        self.stock_name = stock_name
        return self

    def set_quantity(self, quantity: int) -> 'PlaceNormalOrderModel':
        self.quantity = quantity
        return self

    def set_order_type(self, order_type: str) -> 'PlaceNormalOrderModel':
        self.order_type = order_type
        return self

    def execute(self) -> 'PlaceNormalOrder':
        order_id = self.kite_instance.place_order(variety=self.kite_instance.VARIETY_REGULAR, exchange=self.kite_instance.EXCHANGE_NSE,
                                                  tradingsymbol=self.stock_name, transaction_type=self.order_type,
                                                  quantity=self.quantity, product=self.kite_instance.PRODUCT_MIS,
                                                  order_type=self.kite_instance.ORDER_TYPE_MARKET)

        return PlaceNormalOrder(order_id=order_id)
