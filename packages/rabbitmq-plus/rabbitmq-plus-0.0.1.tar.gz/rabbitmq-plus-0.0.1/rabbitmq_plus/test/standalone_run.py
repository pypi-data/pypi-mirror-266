# -*- coding: utf-8 -*-
import logging
from rabbitmq_plus.test.func import test
from rabbitmq_plus.base.producer import Producer
from rabbitmq_plus.base.consumer import ReconnectingConsumer

logger = logging.getLogger("pika.consumer")

mes = dict(a="1111111")

port = 5672
app_id = "TEST_APPLICATION"
host = "127.0.0.1"
username = "opsuser"
password = "Admin@123"
virtual_host = "test"
queue = "test.queur"
heartbeat_queue = "consumer_listen"
retry_exchange = "retry.exchange"
retry_queue = "retry.queue"
retry_routing_key = "retry.queue"
retry_exchange_type = "direct"

producer = Producer(app_id=app_id, username=username, password=password, port=port, host=host,
                    virtual_host=virtual_host, queue=queue, routing_key=queue)
# 启用死信队列，当consumer遇到不能消费的消息，nack后，会自动推送到死信队列
# producer.reset_declare(enable_retry=True, retry_exchange=retry_exchange, retry_queue=retry_queue,
#                        retry_routing_key=retry_routing_key, retry_exchange_type=retry_exchange_type)
# 设置队列的消息的生存时间，属性值必须大于1，即1秒，少于1，属性不生效。
# producer.reset_declare(ttl=1)
producer.publish(message=mes)

# c = ReconnectingConsumer(username=username, password=password, port=port, host=host, virtual_host=virtual_host,
#                          queue=queue, routing_key=queue, heartbeat_queue=heartbeat_queue, callback=test,
#                          enable_retry=True, ttl=1, retry_exchange=retry_exchange, retry_queue=retry_queue,
#                          retry_routing_key=retry_routing_key, retry_exchange_type=retry_exchange_type)
c = ReconnectingConsumer(username=username, password=password, port=port, host=host, virtual_host=virtual_host,
                         queue=queue, routing_key=queue, heartbeat_queue=heartbeat_queue, callback=test)
c.start()
