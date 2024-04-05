# -*- coding: utf-8 -*-
import logging
import traceback
from time import sleep
from json import dumps
from pika.exceptions import *
from pika.spec import BasicProperties
from pika import ConnectionParameters, BlockingConnection
from pika.adapters.blocking_connection import BlockingChannel

from rabbitmq_plus.base.integrated import PiKa
from rabbitmq_plus.base.context import is_current_app
from rabbitmq_plus.base.properties import ProducerParameters

logger = logging.getLogger("pika.producer")


class Producer(ProducerParameters):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._should_reconnect = True
        self._open_channel()

    @property
    def channel(self) -> BlockingChannel:
        return self._channel

    @channel.setter
    def channel(self, channel: BlockingChannel):
        self._channel = channel

    @property
    def connection(self) -> BlockingConnection:
        return self._connection

    @connection.setter
    def connection(self, connection_parameters: ConnectionParameters):
        self._connection = BlockingConnection(connection_parameters)

    def exchange_declare(self):
        logger.info(f'Declare exchange: 【{self.exchange}】')
        # 创建交换类型
        # callback=None : 当 Exchange.DeclareOk 时 调用该方法, 当 nowait=True 该值必须为 None
        # exchange=None: 交换器名称,保持非空,由字母、数字、连字符、下划线、句号组成
        # exchange_type='direct': 交换器类型
        # passive=False: 执行一个声明或检查它是否存在
        # durable=False: RabbitMQ 重启时保持该交换器的持久性,即不会丢失
        # auto_delete=False: 没有队列绑定到该交换器时,自动删除该交换器
        # internal=False: 只能由其它交换器发布-Can only be published to by other exchanges
        # nowait=False: 不需要 Exchange.DeclareOk 的响应-Do not expect an Exchange.DeclareOk response
        # arguments=None: 对该交换器自定义的键/值对, 默认为空
        self.channel.exchange_declare(exchange=self.exchange, durable=True, passive=False,
                                      exchange_type=self.exchange_type)

    def queue_declare(self):
        logger.info(f'Declare queue: 【{self.queue}】')
        # 申明消息队列, 当不确定生产者和消费者哪个先启动时，可以两边重复声明消息队列。
        #          durable: 当 RabbitMQ 重启时,队列保持持久性，默认false
        #          passive: 只检查队列是否存在，并不会创建队列，默认值：false
        #          exclusive：仅允许当前连接访问该队列， 默认false
        #          auto_delete：当消费者取消或者断开连接时, 自动删除该队列， 默认false
        #          nowait： 当 Queue.Declare Ok 时不需要等待， 默认false
        #          arguments：可自定义队列键/值参数，默认None
        arguments = dict()
        if self.enable_retry is True:
            # 设置死信转发的exchange，延迟结束后指向的交换机(死信收容交换机)
            # 如果原有消息的路由key是testA，被发送到业务Exchage中，然后被投递到业务队列QueueA中，
            # 如果该队列没有配置参数x-dead-letter-routing-key，则该消息成为死信后，将保留原有的路由keytestA，如果配置了该参数，
            # 并且值设置为testB，那么该消息成为死信后，路由key将会被替换为testB，然后被抛到死信交换机中
            arguments.update({"x-dead-letter-exchange": self.retry_exchange,
                              "x-dead-letter-routing-key": self.retry_routing_key or self.routing_key})
        # 消息的存活时间，消息过期后会被指向(死信收容交换机)收入死信队列
        if self.ttl >= 1000:
            arguments.update({"x-message-ttl": self.ttl})
        self.channel.queue_declare(queue=self.queue, durable=True, passive=False,
                                   arguments=arguments if arguments else None)

    def bind_queue(self):
        # 绑定队列与exchange
        logger.info("Queue bound.")
        self.channel.queue_bind(queue=self.queue, exchange=self.exchange, routing_key=self.routing_key)

    def publish(self, message: str or list or dict, properties: BasicProperties = None):
        if properties is None:
            properties = self.properties
        if isinstance(message, list):
            for mes in message:
                try:
                    message_new = dumps(mes)
                    logger.info("向队列：<{}>的routing_key: <{}>发送消息为: {}".format(self.queue,
                                                                             self.routing_key, message_new))
                    self.channel.basic_publish(exchange=self.exchange, properties=properties,
                                               routing_key=self.routing_key, body=message_new)
                except Exception as e:
                    logger.error(traceback.format_exc())
                    logger.error(e)
        else:
            try:
                message_new = dumps(message)
                logger.info("向队列：<{}>的routing_key: <{}>发送消息为: {}".format(self.queue,
                                                                         self.routing_key, message_new))
                self.channel.basic_publish(exchange=self.exchange, properties=properties,
                                           routing_key=self.routing_key, body=message_new)
            except Exception as e:
                logger.error(traceback.format_exc())
                logger.error(e)
        self._close()

    def _close(self):
        if self.connection:
            logger.info("消息发送完成，关闭连接{}通道。".format(self.connection))
            # 关闭与rabbitmq server的连接
            self.connection.close()
        else:
            # 正常使用 return_channel 释放通道，归还给pool
            logger.info(f"消息发送完成，释放通道{self.channel}，归还给pool。")
            self.pk.return_channel(self.channel)

    def _open_channel(self):
        while self._should_reconnect:
            try:
                logger.info(f"RabbitMQ Producer Ready connection {self.connection_parameters}.")
                if is_current_app() and isinstance(self.pk, PiKa):
                    # 建立rabbit协议的通道
                    self.channel = self.pk.channel()
                else:
                    # 建立rabbit协议的通道
                    self.connection = self.connection_parameters
                    self.channel = self.connection.channel()
                logger.info(f'RabbitMQ Producer Channel{self.channel} opened.')
                self._was_connected = True
                self._should_reconnect = False
            except (Exception, AMQPChannelError, AMQPConnectionError, AMQPError, StreamLostError) as e:
                logger.error(f'RabbitMQ Producer channel open exception.')
                self._was_connected = False
                self._should_reconnect = True
                reconnect_delay = self._get_reconnect_delay()
                logger.error(traceback.format_exc())
                string = f"RabbitMQ Producer: <{self.url}>连接失败，"
                if str(e):
                    string = string + f"原因: <{e}>，{reconnect_delay}秒后开始尝试连接..."
                else:
                    string = string + f"{reconnect_delay}秒后开始尝试连接..."
                logger.error(string)
                sleep(reconnect_delay)
        self.exchange_declare()
        self.queue_declare()
        self.bind_queue()

    def reset_declare(self, queue: str = None, exchange: str = None, exchange_type: str = None, ttl: int = None,
                      routing_key: str = None, enable_retry: bool = False, retry_routing_key: str = None,
                      retry_exchange: str = None, retry_queue: str = None, retry_exchange_type: str = None):
        self.enable_retry = enable_retry
        if ttl:
            self.ttl = ttl
        if queue:
            self.queue = queue
        if exchange:
            self.exchange = exchange
        if routing_key:
            self.routing_key = self.queue
        if exchange_type:
            self.exchange_type = exchange_type
        if retry_queue:
            self.retry_queue = retry_queue
        if retry_exchange:
            self.retry_exchange = retry_exchange
        if retry_routing_key:
            self.retry_routing_key = self.retry_queue
        if retry_exchange_type:
            self.retry_exchange_type = retry_exchange_type
        self._open_channel()
