from enum import Enum


class OrderSide(Enum):
    SELL = 1
    """ 매도 """
    BUY = 2
    """ 매수 """


class OrderType(Enum):
    LIMIT = 0
    """ 지정가 """
    LIMIT_IOC = 11
    """ 지정가, 즉시(일부)체결 그리고 잔량취소 """
    LIMIT_FOK = 12
    """ 지정가, 즉시 전량 체결 또는 전량취소 """
    LIMIT_CONDITIONAL = 2
    """ 조건부지정가, 지정가 주문을 넣고 장 마감까지 체결되지 않은 경우 동시호가 가격으로 체결 시킴 """
    MARKET = 1
    """ 시장가 """
    MARKET_IOC = 13
    """ 시장가, 즉시 (일부)체결 그리고 잔량취소 """
    MARKET_FOK = 14
    """ 시장가, 즉시 전량체결 또는 전량취소 """
    PRIMARY_PRICE = 3
    """ 최우선지정가, 반대방향의 1차호가로 주문 제출 """
    BEST_PRICE = 4
    """ 최유리지정가, 같은방향의 1차호가로 주문 제출 """
    BEST_PRICE_IOC = 15
    """ 최유리지정가, 즉시 (일부)체결 그리고 잔량취소"""
    BEST_PRICE_FOK = 16
    """ 최유리지정가, 즉시 전량체결 또는 전량취소"""


class OrderRequestType(Enum):
    NEW = 1
    """ 신규주문 """
    MODIFY = 2
    """ 주문수정 """
    CANCEL = 3
    """ 주문취소 """
