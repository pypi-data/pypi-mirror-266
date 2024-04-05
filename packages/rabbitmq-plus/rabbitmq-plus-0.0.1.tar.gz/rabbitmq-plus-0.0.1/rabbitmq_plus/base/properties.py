# -*- coding: utf-8 -*-
from uuid import uuid4
from flask import Flask
from typing import Callable
from datetime import datetime
from pika.spec import BasicProperties
from pika.exchange_type import ExchangeType
from pika import channel, spec, PlainCredentials, ConnectionParameters

from rabbitmq_plus.base.integrated import PiKa
from rabbitmq_plus.base.context import is_current_app, is_callable

__all__ = ['ProducerParameters', 'ConsumerParameters']


class Default(object):
    USERNAME = 'guest'
    PASSWORD = 'guest'

    BLOCKED_CONNECTION_TIMEOUT = 300
    CHANNEL_MAX = channel.MAX_CHANNELS
    CLIENT_PROPERTIES = None
    CONNECTION_ATTEMPTS = 1
    FRAME_MAX = spec.FRAME_MAX_SIZE
    HEARTBEAT_TIMEOUT = 600  # None accepts server's proposal
    HOST = '127.0.0.1'
    LOCALE = 'en_US'
    PORT = 5672
    RETRY_DELAY = 2.0
    SOCKET_TIMEOUT = 10.0  # socket.connect() timeout
    STACK_TIMEOUT = 15.0  # full-stack TCP/[SSl]/AMQP bring-up timeout
    SSL = False
    SSL_OPTIONS = None
    SSL_PORT = 5671
    VIRTUAL_HOST = '/'
    TCP_OPTIONS = None
    EXCHANGE = 'amq.direct'
    EXCHANGE_TYPE = ExchangeType.direct.value
    QUEUE = 'test.queue'
    RETRY = "retry.queue"
    HEARTBEAT = "heartbeat.queue"
    RETRY_EXCHANGE = "retry.exchange"
    DELIVERY_MODE = 2  # delivery_mode: 1 为非持久化存储，2 为持久化存储
    CONTENT_TYPE = "application/json"
    CONTENT_ENCODING = 'utf-8'
    APPLICATION_ID = "test.application"


class PublicParameters(object):

    def __init__(self, username: str = None, password: str = None, port: int = None, exchange: str = None,
                 host: str = None, exchange_type: str = None, routing_key: str = None, queue: str = None,
                 virtual_host: str = None, heartbeat_queue: str = None, retry_queue: str = None, ttl: int = 0,
                 retry_exchange: str = None, retry_exchange_type: str = None, enable_retry: bool = False,
                 retry_routing_key: str = None):
        self._channel = None
        self._connection = None
        self._reconnect_delay = 0
        self._was_connected = False
        self._should_reconnect = False
        self._port = port or Default.PORT
        self._host = host or Default.HOST
        self._queue = queue or Default.QUEUE
        self._username = username or Default.USERNAME
        self._password = password or Default.PASSWORD
        self._exchange = exchange or Default.EXCHANGE
        self._routing_key = routing_key or self._queue
        self._retry_queue = retry_queue or Default.RETRY
        self._virtual_host = virtual_host or Default.VIRTUAL_HOST
        self._exchange_type = exchange_type or Default.EXCHANGE_TYPE
        self._heartbeat_queue = heartbeat_queue or Default.HEARTBEAT
        self._retry_exchange = retry_exchange or Default.RETRY_EXCHANGE
        self._retry_routing_key = retry_routing_key or self._retry_queue
        self._ttl = ttl * 1000 if isinstance(ttl, int) and ttl >= 1 else 0
        self._credentials = PlainCredentials(self._username, self._password)
        self._retry_exchange_type = retry_exchange_type or Default.EXCHANGE_TYPE
        self._enable_retry = enable_retry if isinstance(enable_retry, bool) else False

    @property
    def url(self) -> str:
        return f"amqp://{self._username}:{self._password}@{self._host}:{self._port}/{self._virtual_host}"

    @property
    def ttl(self) -> int:
        return self._ttl

    @ttl.setter
    def ttl(self, ttl: int):
        if isinstance(ttl, int) and ttl >= 1:
            # ttl的单位是us，秒转成 us，需要 * 1000
            self._ttl = ttl * 1000
        else:
            raise ValueError("ttl type is Integer and value must be greater than 1")

    @property
    def enable_retry(self) -> bool:
        return self._enable_retry

    @enable_retry.setter
    def enable_retry(self, enable_retry: bool):
        if isinstance(enable_retry, bool):
            self._enable_retry = enable_retry
        else:
            raise ValueError("Property enable_retry must be of type boolean.")

    @property
    def queue(self) -> str:
        return self._queue

    @queue.setter
    def queue(self, queue_name: str):
        self._queue = queue_name

    @property
    def retry_queue(self) -> str:
        return self._retry_queue

    @retry_queue.setter
    def retry_queue(self, queue_name: str):
        self._retry_queue = queue_name

    @property
    def exchange(self) -> str:
        return self._exchange

    @exchange.setter
    def exchange(self, exchange_name: str):
        self._exchange = exchange_name

    @property
    def retry_exchange(self) -> str:
        return self._retry_exchange

    @retry_exchange.setter
    def retry_exchange(self, exchange_name: str):
        self._retry_exchange = exchange_name

    @property
    def routing_key(self) -> str:
        return self._routing_key

    @routing_key.setter
    def routing_key(self, routing_key: str):
        self._routing_key = routing_key

    @property
    def retry_routing_key(self) -> str:
        return self._retry_routing_key

    @retry_routing_key.setter
    def retry_routing_key(self, routing_key: str):
        self._retry_routing_key = routing_key

    @property
    def virtual_host(self) -> str:
        return self._virtual_host

    @virtual_host.setter
    def virtual_host(self, virtual_host: str):
        self._virtual_host = virtual_host

    @property
    def exchange_type(self) -> str:
        return self._exchange_type

    @exchange_type.setter
    def exchange_type(self, exchange_type: str):
        self._exchange_type = exchange_type

    @property
    def retry_exchange_type(self) -> str:
        return self._retry_exchange_type

    @retry_exchange_type.setter
    def retry_exchange_type(self, exchange_type: str):
        self._retry_exchange_type = exchange_type

    @staticmethod
    def _get_default_message_id() -> str:
        return str(uuid4())

    @staticmethod
    def _get_default_app_id() -> str:
        return Default.APPLICATION_ID

    @property
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, username: str):
        self._username = username

    @property
    def password(self) -> str:
        return self._password

    @password.setter
    def password(self, password: str):
        self._password = password

    @staticmethod
    def _get_default_user_id() -> str:
        return Default.USERNAME

    @staticmethod
    def _get_current_timestamp() -> int:
        return int(datetime.now().timestamp() * 1000)

    def _get_default_connection_parameters(self) -> ConnectionParameters:
        # 从RabbitMQ 3.5.5开始，代理的默认心跳超时时间从580秒减少到60秒，
        # 因此在运行 Pika 连接的同一线程中执行冗长处理的应用程序可能会由于心跳超时而意外断开连接。
        # 在这里，我们为心跳超时指定了一个明确的下限。
        return ConnectionParameters(host=self._host,
                                    port=self._port,
                                    credentials=self._credentials,
                                    heartbeat=Default.HEARTBEAT_TIMEOUT,
                                    virtual_host=self._virtual_host,
                                    blocked_connection_timeout=Default.BLOCKED_CONNECTION_TIMEOUT)

    def _get_reconnect_delay(self):
        if self._was_connected:
            self._reconnect_delay = 0
        else:
            self._reconnect_delay = self._reconnect_delay + 1
        if self._reconnect_delay > 30:
            self._reconnect_delay = 30
        return self._reconnect_delay


class ProducerParameters(PublicParameters):
    def __init__(self, app_id: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pk = None
        self._app_id = app_id
        self._properties = BasicProperties()

    def init_pk(self, pk: PiKa):
        if isinstance(pk, PiKa):
            self.pk = pk

    @property
    def connection_parameters(self) -> ConnectionParameters:
        if is_current_app() and isinstance(self.pk, PiKa):
            con_params = self.pk.pika_connection_params
        else:
            con_params = self._get_default_connection_parameters()
        return con_params

    @property
    def app_id(self) -> str:
        return self._app_id

    @app_id.setter
    def app_id(self, app_id: str):
        self._app_id = app_id

    @property
    def properties(self) -> BasicProperties:
        if self._properties.user_id is None:
            self._properties.user_id = self.username
        if self._properties.app_id is None:
            self._properties.app_id = self.app_id or self._get_default_app_id()
        if self._properties.message_id is None:
            self._properties.message_id = self._get_default_message_id()
        if self._properties.content_type is None:
            self._properties.content_type = Default.CONTENT_TYPE
        if self._properties.content_encoding is None:
            self._properties.content_encoding = Default.CONTENT_ENCODING
        if self._properties.timestamp is None:
            # 给消息打上时间戳，采用utc 零时区
            self._properties.timestamp = self._get_current_timestamp()
        if self._properties.delivery_mode is None:
            # delivery_mode: 1 为非持久化存储，2 为持久化存储
            self._properties.delivery_mode = Default.DELIVERY_MODE
        return self._properties


class ConsumerParameters(PublicParameters):

    def __init__(self, app: Flask = None, callback: Callable = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._app = app
        self._closing = False
        self._consuming = False
        self._consumer_tag = None
        self._callback = callback

    @property
    def closing(self) -> bool:
        return self._closing

    @closing.setter
    def closing(self, status: bool):
        self._closing = status

    @property
    def consumer_tag(self) -> str:
        return self._consumer_tag

    @consumer_tag.setter
    def consumer_tag(self, consumer_tag: str):
        self._consumer_tag = consumer_tag

    @property
    def heartbeat_queue(self) -> str:
        return self._heartbeat_queue

    @heartbeat_queue.setter
    def heartbeat_queue(self, queue_name: str):
        self._heartbeat_queue = queue_name

    @property
    def callback(self) -> Callable:
        return self._callback

    @callback.setter
    def callback(self, callback_name: Callable):
        if is_callable(handle=callback_name):
            self._callback = callback_name
        else:
            raise ValueError(f"{callback_name} is not callable.")

    @property
    def app(self) -> Flask:
        return self._app

    @app.setter
    def app(self, app: Flask):
        if isinstance(app, Flask):
            self._app = app
        else:
            raise ValueError(f"{app} is non-flask application, Don't support.")
