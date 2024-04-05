# -*- coding: utf-8 -*-
import time
import pika
import logging
import traceback
from json import loads
from flask import Flask
from pika.frame import Method
from pika.channel import Channel
from pika import SelectConnection
from pika.connection import Connection
from pika.spec import Basic, BasicProperties

from rabbitmq_plus.base.properties import ConsumerParameters

logger = logging.getLogger("pika.consumer")


class AsyncConsumer(ConsumerParameters):
    """This is an example consumer that will handle unexpected interactions
    with RabbitMQ such as channel and connection closures.
    If RabbitMQ closes the connection, this class will stop and indicate
    that reconnection is necessary. You should look at the output, as
    there are limited reasons why the connection may be closed, which
    usually are tied to permission related issues or socket timeouts.
    If the channel is closed, it will indicate a problem with one of the
    commands that were issued and that should surface in the output as well.
    """

    def __init__(self, *args, **kwargs):
        """Create a new instance of the consumer class, passing in the AMQP
        URL used to connect to RabbitMQ.
        """
        super().__init__(*args, **kwargs)
        # In production, experiment with higher prefetch values
        # for higher consumer throughput
        self._prefetch_count = 1

    def connect(self):
        """This method connects to RabbitMQ, returning the connection handle.
        When the connection is established, the on_connection_open method
        will be invoked by pika.
        :rtype: pika.SelectConnection
        """
        logger.info('RabbitMQ Consumer Connecting to %s', self.url)
        return pika.SelectConnection(parameters=pika.URLParameters(self.url), on_open_callback=self.on_connection_open,
                                     on_open_error_callback=self.on_connection_open_error,
                                     on_close_callback=self.on_connection_closed)

    def close_connection(self):
        self._consuming = False
        if self._connection.is_closing or self._connection.is_closed:
            logger.info('Connection is closing or already closed')
        else:
            logger.info('Closing connection')
            self._connection.close()

    def on_connection_open(self, _unused_connection: SelectConnection):
        """This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.
        :param pika.SelectConnection _unused_connection: The connection
        """
        logger.info('Connection opened')
        self.open_channel()

    def on_connection_open_error(self, _unused_connection: SelectConnection, err: Exception):
        """This method is called by pika if the connection to RabbitMQ
        can't be established.
        :param pika.SelectConnection _unused_connection: The connection
        :param Exception err: The error
        """
        logger.error('Connection open failed: %s', err)
        self.closing = True
        raise ConnectionError("RabbitMQ Consumer connection exception.")
        # self.reconnect()

    def on_connection_closed(self, _unused_connection: Connection, reason: Exception):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.
        :param pika.connection.Connection _unused_connection: The closed connection obj
        :param Exception reason: exception representing reason for loss of
            connection.
        """
        if self.closing:
            self._connection.ioloop.stop()
        else:
            logger.warning('Connection closed, reconnect necessary: %s', reason)
            self.closing = True
            raise ConnectionError("RabbitMQ Consumer connection exception.")
            # self.reconnect()

    def reconnect(self):
        """Will be invoked if the connection can't be opened or is
        closed. Indicates that a reconnect is necessary then stops the
        ioloop.
        """
        self._should_reconnect = True
        self.stop()

    def open_channel(self):
        """Open a new channel with RabbitMQ by issuing the Channel.Open RPC
        command. When RabbitMQ responds that the channel is open, the
        on_channel_open callback will be invoked by pika.
        """
        logger.info('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel: Channel):
        """This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.
        Since the channel is now open, we'll declare the exchange to use.
        :param pika.channel.Channel channel: The channel object
        """
        logger.info(f'RabbitMQ Consumer Channel{channel} opened.')
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange()

    def add_on_channel_close_callback(self):
        """This method tells pika to call the on_channel_closed method if
        RabbitMQ unexpectedly closes the channel.
        """
        logger.info('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel: Channel, reason: Exception):
        """Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.
        :param pika.channel.Channel channel: The closed channel
        :param Exception reason: why the channel was closed
        """
        logger.warning('Channel %i was closed: %s', channel, reason)
        self.close_connection()

    def setup_exchange(self):
        """Setup the exchange on RabbitMQ by invoking the Exchange.Declare RPC
        command. When it is complete, the on_exchange_declare_ok method will
        be invoked by pika.
        """
        logger.info('Declaring Exchange: 【%s】', self.exchange)
        self._channel.exchange_declare(exchange=self.exchange, exchange_type=self.exchange_type,
                                       callback=self.on_exchange_declare_ok, durable=True, passive=False)

    def on_exchange_declare_ok(self, _unused_frame: Method):
        """Invoked by pika when RabbitMQ has finished the Exchange.Declare RPC
        command.
        :param pika.Frame.Method _unused_frame: Exchange.DeclareOk response frame
        """
        logger.info('Exchange declared: %s', self.exchange)
        self.setup_queue()

    def setup_queue(self):
        """Setup the queue on RabbitMQ by invoking the Queue.Declare RPC
        command. When it is complete, the on_queue_declare_ok method will
        be invoked by pika.
        """
        logger.info('Declaring Heartbeat queue 【%s】', self.heartbeat_queue)
        self._channel.queue_declare(queue=self.heartbeat_queue, durable=True, passive=False, auto_delete=True,
                                    callback=self.on_heartbeat_queue_declare_ok)
        arguments = dict()
        if self.enable_retry is True:
            # 设置死信转发的exchange，延迟结束后指向的交换机(死信收容交换机)
            # 如果原有消息的路由key是testA，被发送到业务Exchage中，然后被投递到业务队列QueueA中，
            # 如果该队列没有配置参数x-dead-letter-routing-key，则该消息成为死信后，将保留原有的路由keytestA，如果配置了该参数，
            # 并且值设置为testB，那么该消息成为死信后，路由key将会被替换为testB，然后被抛到死信交换机中
            arguments.update({"x-dead-letter-exchange": self.retry_exchange,
                              "x-dead-letter-routing-key": self.retry_routing_key or self.routing_key})
            self.declare_retry_queue()
        # 消息的存活时间，消息过期后会被指向(死信收容交换机)收入死信队列
        if self.ttl >= 1000:
            arguments.update({"x-message-ttl": self.ttl})
        logger.info('Declaring Queue 【%s】', self.queue)
        self._channel.queue_declare(queue=self.queue, durable=True, passive=False, callback=self.on_queue_declare_ok,
                                    arguments=arguments if arguments else None)

    def declare_retry_queue(self):
        """
        创建异常交换器和队列，用于存放没有正常处理的消息。
        :return:
        """
        logger.info('Declaring Retry exchange: 【%s】', self.retry_exchange)
        self._channel.exchange_declare(exchange=self.retry_exchange, exchange_type=self.retry_exchange_type,
                                       durable=True, passive=False)
        logger.info('Declaring Retry queue 【%s】', self.retry_queue)
        self._channel.queue_declare(queue=self.retry_queue, durable=True, passive=False)
        logger.info('Binding Retry exchange %s to Retry queue %s with Routing Key %s',
                    self.retry_exchange, self.retry_queue, self.retry_routing_key)
        self._channel.queue_bind(
            queue=self.retry_queue, exchange=self.retry_exchange, routing_key=self.retry_routing_key)

    def on_heartbeat_queue_declare_ok(self, _unused_frame: Method):
        """Method invoked by pika when the Queue.Declare RPC call made in
        setup_queue has completed. In this method we will bind the queue
        and exchange together with the routing key by issuing the Queue.Bind
        RPC command. When this command is complete, the on_bind_ok method will
        be invoked by pika.
        :param pika.frame.Method _unused_frame: The Queue.DeclareOk frame
        """
        logger.info('Binding Exchange %s to Heartbeat queue %s with Routing key %s',
                    self.exchange, self.heartbeat_queue, self.heartbeat_queue)
        self._channel.queue_bind(queue=self.heartbeat_queue, exchange=self.exchange,
                                 routing_key=self.heartbeat_queue, callback=self.on_heartbeat_bind_ok)

    def on_queue_declare_ok(self, _unused_frame: Method):
        """Method invoked by pika when the Queue.Declare RPC call made in
        setup_queue has completed. In this method we will bind the queue
        and exchange together with the routing key by issuing the Queue.Bind
        RPC command. When this command is complete, the on_bind_ok method will
        be invoked by pika.
        :param pika.frame.Method _unused_frame: The Queue.DeclareOk frame
        """
        logger.info('Binding Exchange %s to Queue %s with Routing key %s', self.exchange, self.queue, self.routing_key)
        self._channel.queue_bind(queue=self.queue, exchange=self.exchange, routing_key=self.routing_key,
                                 callback=self.on_bind_ok)

    def on_bind_ok(self, _unused_frame: Method):
        """Invoked by pika when the Queue.Bind method has completed. At this
        point we will set the prefetch count for the channel.
        :param pika.frame.Method _unused_frame: The Queue.BindOk response frame
        """
        logger.info('Queue bound: %s', self.queue)
        self.set_qos()

    def on_heartbeat_bind_ok(self, _unused_frame: Method):
        """Invoked by pika when the Queue.Bind method has completed. At this
        point we will set the prefetch count for the channel.
        :param pika.frame.Method _unused_frame: The Queue.BindOk response frame
        """
        logger.info('Heartbeat queue bound: %s', self.heartbeat_queue)

    def set_qos(self):
        """This method sets up the consumer prefetch to only be delivered
        one message at a time. The consumer must acknowledge this message
        before RabbitMQ will deliver another one. You should experiment
        with different prefetch values to achieve desired performance.
        """
        self._channel.basic_qos(prefetch_count=self._prefetch_count, callback=self.on_basic_qos_ok)

    def reject_message(self, delivery_tag: int, message_id: str, app_id: str, body: bytes):
        """Reject an incoming message. This method allows a client to reject a message.
           It can be used to interrupt and cancel large incoming messages,
           or return untreatable messages to their original queue.
           Parameters:	delivery-tag (int) – The server-assigned delivery tag
                        requeue (bool) – If requeue is true, the server will attempt to requeue the message.
                        If requeue is false or the requeue attempt fails the messages are discarded or dead-lettered.
        """
        logger.warning(
            f"Message: # {delivery_tag} ID: {message_id} from {app_id}: {body} will be reset to the original queue.")
        self._channel.basic_reject(delivery_tag=delivery_tag, requeue=True)

    def nack_message(self, delivery_tag: int, app_id: str, body: bytes):
        """This method allows a client to reject one or more incoming messages. It can be used to interrupt and cancel
           large incoming messages, or return untreatable messages to their original queue.
           Parameters:	delivery-tag (int) – The server-assigned delivery tag
                        multiple (bool) – If set to True, the delivery tag is treated as “up to and including”,
                                          so that multiple messages can be acknowledged with a single method.
                                          If set to False, the delivery tag refers to a single message.
                                          If the multiple field is 1, and the delivery tag is 0,
                                          this indicates acknowledgement of all outstanding messages.
                        requeue (bool) – If requeue is true, the server will attempt to requeue the message.
                                         If requeue is false or the requeue attempt fails the messages are
                                         discarded or dead-lettered.
        """
        logger.warning(f"Message: # {delivery_tag} from {app_id}: {body} will be reset to the original queue.")
        self._channel.basic_nack(delivery_tag=delivery_tag, multiple=False, requeue=True)

    def on_basic_qos_ok(self, _unused_frame: Method):
        """Invoked by pika when the Basic.QoS method has completed. At this
        point we will start consuming messages by calling start_consuming
        which will invoke the needed RPC commands to start the process.
        :param pika.frame.Method _unused_frame: The Basic.QosOk response frame
        """
        logger.info('QOS set to: %d', self._prefetch_count)
        self.start_consuming()

    def start_consuming(self):
        """This method sets up the consumer by first calling
        add_on_cancel_callback so that the object is notified if RabbitMQ
        cancels the consumer. It then issues the Basic.Consume RPC command
        which returns the consumer tag that is used to uniquely identify the
        consumer with RabbitMQ. We keep the value to use it when we want to
        cancel consuming. The on_message method is passed in as a callback pika
        will invoke when a message is fully received.
        """
        logger.info('Issuing consumer related RPC commands')
        self.add_on_cancel_callback()
        self.consumer_tag = self._channel.basic_consume(queue=self.queue, on_message_callback=self.on_message)
        self._was_connected = True
        self._consuming = True

    def add_on_cancel_callback(self):
        """Add a callback that will be invoked if RabbitMQ cancels the consumer
        for some reason. If RabbitMQ does cancel the consumer,
        on_consumer_cancelled will be invoked by pika.
        """
        logger.info('Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(callback=self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame: Method):
        """Invoked by pika when RabbitMQ sends a Basic.Cancel for a consumer
        receiving messages.
        :param pika.frame.Method method_frame: The Basic.Cancel frame
        """
        logger.info('Consumer was cancelled remotely, shutting down: %r', method_frame)
        if self._channel:
            self._channel.close()

    @classmethod
    def rich_properties(cls, properties: BasicProperties) -> BasicProperties:
        if properties.app_id is None:
            setattr(properties, "app_id", cls._get_default_app_id())
        if properties.user_id is None:
            setattr(properties, "user_id", cls._get_default_user_id())
        if properties.timestamp is None:
            setattr(properties, "timestamp", cls._get_current_timestamp())
        if properties.message_id is None:
            setattr(properties, "message_id", cls._get_default_message_id())
        return properties

    def on_message(self, _unused_channel: Method, basic_deliver: Basic.Deliver, properties: BasicProperties,
                   body: bytes):
        """Invoked by pika when a message is delivered from RabbitMQ. The
        channel is passed for your convenience. The basic_deliver object that
        is passed in carries the exchange, routing key, delivery tag and
        a redelivered flag for the message. The properties passed in is an
        instance of BasicProperties with the message properties and the body
        is the message that was sent.
        :param pika.channel.Channel _unused_channel: The channel object
        :param pika.Spec.Basic.Deliver basic_deliver: basic_deliver method
        :param pika.Spec.BasicProperties properties: properties
        :param bytes body: The message body
        """
        properties = self.rich_properties(properties=properties)
        logger.info('Received message # %s ID: %s from %s: %s',
                    basic_deliver.delivery_tag, properties.message_id, properties.app_id, body)
        if self.callback:
            try:
                body_new = loads(str(body, encoding="utf-8"))
                if self.app:
                    self.callback(self.app, body_new, self.consumer_tag, basic_deliver, properties)
                else:
                    self.callback(body_new, self.consumer_tag, basic_deliver, properties)
                self.acknowledge_message(delivery_tag=basic_deliver.delivery_tag, message_id=properties.message_id)
            except Exception as e:
                logger.error(traceback.format_exc())
                logger.error(e)
                self.reject_message(delivery_tag=basic_deliver.delivery_tag, message_id=properties.message_id,
                                    app_id=properties.app_id, body=body)
        else:
            logger.warning("Current consumer don't configured handle function.")
            self.reject_message(delivery_tag=basic_deliver.delivery_tag, message_id=properties.message_id,
                                app_id=properties.app_id, body=body)

    def acknowledge_message(self, delivery_tag: int, message_id: str):
        """Acknowledge the message delivery from RabbitMQ by sending a
        Basic.Ack RPC method for the delivery tag.
        :param int delivery_tag: The delivery tag from the Basic.Deliver frame
        :param str message_id: The message id
        """
        logger.info('Acknowledging message # %s ID: %s', delivery_tag, message_id)
        self._channel.basic_ack(delivery_tag=delivery_tag)

    def stop_consuming(self):
        """Tell RabbitMQ that you would like to stop consuming by sending the
        Basic.Cancel RPC command.
        """
        if self._channel:
            logger.info('Sending a Basic.Cancel RPC command to RabbitMQ')
            self._channel.basic_cancel(consumer_tag=self.consumer_tag, callback=self.on_cancel_ok)

    def on_cancel_ok(self, _unused_frame: Method):
        """This method is invoked by pika when RabbitMQ acknowledges the
        cancellation of a consumer. At this point we will close the channel.
        This will invoke the on_channel_closed method once the channel has been
        closed, which will in-turn close the connection.
        :param pika.frame.Method _unused_frame: The Basic.CancelOk frame
        """
        self._consuming = False
        logger.info('RabbitMQ acknowledged the cancellation of the consumer: %s', self.consumer_tag)
        self.close_channel()

    def close_channel(self):
        """Call to close the channel with RabbitMQ cleanly by issuing the
        Channel.Close RPC command.
        """
        logger.info('Closing the channel')
        self._channel.close()

    def start(self):
        """Run the example consumer by connecting to RabbitMQ and then
        starting the IOLoop to block and allow the SelectConnection to operate.
        """
        self._connection = self.connect()
        self._connection.ioloop.start()

    def stop(self):
        """Cleanly shutdown the connection to RabbitMQ by stopping the consumer
        with RabbitMQ. When RabbitMQ confirms the cancellation, on_cancelok
        will be invoked by pika, which will then closing the channel and
        connection. The IOLoop is started again because this method is invoked
        when CTRL-C is pressed raising a KeyboardInterrupt exception. This
        exception stops the IOLoop which needs to be running for pika to
        communicate with RabbitMQ. All of the commands issued prior to starting
        the IOLoop will be buffered but not processed.
        """
        if self.closing:
            logger.info('Stopping')
            if self._consuming:
                self.stop_consuming()
                self._connection.ioloop.start()
            else:
                self._connection.ioloop.stop()
                self.closing = False
            logger.info('Stopped')


class ReconnectingConsumer(AsyncConsumer):
    """This is an example consumer that will reconnect if the nested
    ExampleConsumer indicates that a reconnect is necessary.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._reconnect_delay = 0

    def run(self, app: Flask = None):
        if app is not None:
            self.app = app
        flag = 2
        while flag:
            try:
                self.start()
            except KeyboardInterrupt:
                self.stop()
                break
            except OSError as e:
                reconnect_delay = self._get_reconnect_delay()
                logger.error(traceback.format_exc())
                logger.error(f"RabbitMQ Consumer: <{self.url}>连接失败，原因: <{e}>，{reconnect_delay}秒后开始尝试第<{flag}>次连接...")
                flag = flag + 1
                time.sleep(reconnect_delay)
