import  numpy as np

from typing import Any, Sequence
import datetime
from event import Event, EventEngine
from event import (
    EVENT_TICK,
    EVENT_ORDER,
    EVENT_TRADE,
    EVENT_POSITION,
    EVENT_ACCOUNT,
    EVENT_CONTRACT,
)
from object import (
    TickData,
    OrderData,
    PositionData,
    AccountData,
    OrderRequest,
    SubscribeRequest,
)


class Gateway():
    def __init__(self,event_engine,code,exchange):
        self.event_engine=event_engine
        self.code=code
        self.exchange=exchange
        self.init_price=round(np.random.lognormal(mean=3,sigma=1,size=1)[0],2)


        self.tick = TickData(self.code, self.exchange, datetime.datetime.now())

    def on_event(self, type: str, data: Any = None):
        """
        General event push.
        """
        event = Event(type, data)
        self.event_engine.put(event)

    def generate_Tick(self):

        self.tick.name='stock'
        self.tick.open_price=self.init_price
        self.tick.high_price=self.init_price+3
        self.tick.low_price=self.init_price-3
        self.tick.last_price=self.init_price+round(np.random.normal(0,1,size=1)[0],2)
        self.tick.bid_price_1=self.tick.last_price+0.1
        self.tick.ask_price_1=self.tick.last_price-1
        self.tick.bid_volume_1=(round(np.random.normal(2000,500,1)[0],0)//100)*100
        self.tick.ask_volume_1=(round(np.random.normal(2000,500,1)[0],0)//100)*100
        self.tick.datetime=datetime.datetime.now()

        self.on_event(EVENT_TICK,self.tick)

if __name__=='__main__':
    gateway=Gateway('0001','123')
    gateway.generate_Tick()