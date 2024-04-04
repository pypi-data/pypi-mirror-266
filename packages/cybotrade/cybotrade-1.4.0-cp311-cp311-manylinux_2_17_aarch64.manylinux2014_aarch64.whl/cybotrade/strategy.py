import logging
import collections

from typing import Any, List, Dict

from .models import FloatWithTime, OpenedTrade, OrderUpdate

class Strategy:
    """
    This class is a handler that will be used by the Runtime to handle events such as
    `on_candle_closed`, `on_execution_update`, etc. The is a base class and every new strategy
    should be inheriting this class and override the methods.
    """

    logger = logging
    LOG_FORMAT = (
        "%(levelname)s %(name)s %(asctime)-15s %(filename)s:%(lineno)d %(message)s"
    )
    data_map: Dict[str, collections.deque] = {}

    def __init__(
            self,
            log_level: int = logging.INFO,
            handlers: List[logging.Handler] = None,
    ):
        if handlers is None:
            handlers = []
        """
        Set up the logger
        """
        if len(handlers) == 0:
            default_handler = logging.StreamHandler()
            default_handler.setFormatter(logging.Formatter(self.LOG_FORMAT))
            handlers.append(default_handler)

        logging.root.setLevel(log_level)
        for handler in handlers:
            logging.root.addHandler(handler)

    def get_data_map(self):
        return self.data_map
    
    async def initialize_ringbuffer(self, topics, deque_length, data):
        for topic in topics:
            self.data_map[topic] = collections.deque(maxlen=deque_length)
            if topic in data:
                self.data_map[topic].extend(data[topic])

        logging.info("Successfully initialized ringbuffer for data")

    async def update_ringbuffer(self, topic, data_list):
        for data in data_list:
            if topic in self.data_map:
                if len(self.data_map[topic]) < 1:
                    self.data_map[topic].append(data) 

                topic_list = self.data_map[topic][-1]
                try:
                    if data["end_time"] == topic_list["end_time"]:
                        self.data_map[topic].pop()
                        self.data_map[topic].append(data)
                    else:
                        self.data_map[topic].append(data)
                except Exception as e:
                    logging.error(f"Missing end_time parameter in data: {data}\nInform the Cybotrade team in regards to this issue\n");
                    raise e

    async def set_param(self, identifier, value):
        """
        Used to set up params for the strategy
        """
        logging.info(f"Setting {identifier} to {value}")
    
    async def on_init(self, strategy):
        logging.info("[on_init] Strategy successfully started.")

    async def on_trade(self, strategy, trade: OpenedTrade):
        logging.info(f"[on_trade] Received opened trade: {trade.__repr__()}")

    async def on_market_update(self, strategy, equity, available_balance):
        logging.info(
            f"[on_market_update] Received market update: equity({equity.__repr__()}), available_balance({available_balance.__repr__()})")

    async def on_order_update(self, strategy, update):
        logging.info(f"[on_order_update] Received order update: {update.__repr__()}")

    async def on_active_order_interval(self, strategy, active_orders):
        logging.info(f"[on_active_order_interval] Received active orders: {active_orders.__repr__()}")

    async def on_backtest_complete(self, strategy):
        logging.info("[on_backtest_complete] Backtest completed.")
