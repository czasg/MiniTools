import logging
import functools

from pika import PlainCredentials, ConnectionParameters, BlockingConnection, BasicProperties
from typing import Callable

logger = logging.getLogger(__name__)


class RabbitMQ:

    def __init__(self,
                 queue: str,
                 conn_auth: tuple,
                 conn_params: dict = None or {},
                 exchange_params: dict = None or {},
                 **kwargs):
        credentials = PlainCredentials(*conn_auth)
        parameters = ConnectionParameters(credentials=credentials, **conn_params)
        connection = BlockingConnection(parameters)
        channel = connection.channel()

        exchange = exchange_params.pop("exchange") if "exchange" in exchange_params else "minitools"
        auto_delete = kwargs.get("auto_delete", False)
        routing_key = kwargs.get("routing_key")
        requeue = kwargs.get("requeue", True)
        exchange_params.setdefault("durable", True)
        exchange_params.setdefault("auto_delete", auto_delete)

        channel.exchange_declare(exchange, **exchange_params)
        channel.queue_declare(queue=queue, auto_delete=auto_delete)
        channel.queue_bind(queue=queue, exchange=exchange, routing_key=routing_key)
        channel.basic_qos(prefetch_count=1)

        self.queue = queue
        self.requeue = requeue
        self.channel = channel
        self.exchange = exchange
        self.connection = connection
        self.routing_key = routing_key

    def start_consuming(self, callback: Callable = lambda *args: False):
        on_message_callback = functools.partial(self.on_message, callback)
        self.channel.basic_consume(self.queue, on_message_callback)
        self.channel.start_consuming()

    def on_message(self, callback, _unused_channel, basic_deliver, properties, body):
        true_or_false = callback(body.decode())  # type: bool
        assert isinstance(true_or_false, bool), "you need return data of `bool`"
        if true_or_false:
            _unused_channel.basic_ack(delivery_tag=basic_deliver.delivery_tag)
        else:
            _unused_channel.basic_ack(delivery_tag=basic_deliver.delivery_tag, requeue=self.requeue)

    def push(self, data: str, priority: int = None, exchange=None, routing_key=None, **kwargs):
        kwargs.setdefault("delivery_mode", 2)
        self.channel.basic_publish(
            exchange=exchange or self.exchange,
            routing_key=routing_key or self.routing_key,
            body=data,
            properties=BasicProperties(priority=priority, **kwargs)
        )
