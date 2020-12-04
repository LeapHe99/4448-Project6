"""
"""

from abc import ABC
from typing import Any, Sequence

from event import Event, EventEngine
from gateway import Gateway

from object import (
    OrderRequest,
    SubscribeRequest,
)



class MainEngine:

    def __init__(self, event_engine: EventEngine = None):
        """"""
        if event_engine:
            self.event_engine = event_engine
        else:
            self.event_engine = EventEngine()
        self.event_engine.start()

        self.engines = {'Event':self.event_engine}
        self.exchanges = []


    def add_engine(self, engine_class: Any):
        """
        Add function engine.
        """
        engine = engine_class(self, self.event_engine)
        # print(engine.engine_name)
        self.engines[engine.engine_name] = engine
        return engine


    def subscribe(self, req:OrderRequest ):
        """
        Subscribe tick data update of a specific gateway.
        """


        gateway = Gateway(self.event_engine,req.symbol, req.exchange)
        gateway.generate_Tick()


    def send_order(self, req: OrderRequest, ):
        """
        Send new order request
        """
        self.subscribe(req)


        self.event_engine.put(req)


    def close(self):
        """
        Make sure every gateway and app is closed properly before
        programme exit.
        """
        # Stop event engine first to prevent new timer event.
        self.event_engine.stop()


class BaseEngine(ABC):
    """
    Abstract class for implementing an function engine.
    """

    def __init__(
        self,
        main_engine: MainEngine,
        event_engine: EventEngine,
        engine_name: str,
    ):
        """"""
        self.main_engine = main_engine
        self.event_engine = event_engine
        self.engine_name = engine_name

    def close(self):
        """"""
        pass

