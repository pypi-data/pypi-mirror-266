# -*- coding: utf-8 -*-
from time import sleep
from flask import Flask
from multiprocessing.pool import ThreadPool

from rabbitmq_plus.test.func import test
from rabbitmq_plus.base.integrated import PiKa
from rabbitmq_plus.base.producer import Producer
from rabbitmq_plus.base.consumer import ReconnectingConsumer

pool = ThreadPool(processes=5)
app = Flask(import_name="Flask")

port = "5672"
host = "127.0.01"
app_id = "TEST_APPLICATION"
username = "opsuser"
password = "Admin@123"
virtual_host = "test"
queue = "test.queue"
heartbeat_queue = "comsumer_listen"
exchange = "amq.direct"
exchange_type = "direct"

app.config["FLASK_PIKA_PARAMS"] = {
    "host": host,
    "username": username,
    "password": password,
    "port": port,
    "virtual_host": virtual_host,
}

app.config["FLASK_PIKA_POOL_PARAMS"] = None


def consumer() -> ReconnectingConsumer:
    sleep(5)
    _consumer = ReconnectingConsumer(virtual_host=virtual_host, queue=queue, routing_key=queue, exchange=exchange,
                                     heartbeat_queue=heartbeat_queue, exchange_type=exchange_type, callback=test)
    return _consumer


def register_consumer():
    pool.apply_async(consumer().start)


def push():
    pk = PiKa()
    pk.init_app(app)
    mes = dict(a="1111111")
    producer = Producer(app_id=app_id, username=username, password=password, port=port, host=host,
                        virtual_host=virtual_host, queue=queue, routing_key=queue)
    producer.init_pk(pk=pk)
    producer.publish(message=mes)


# if __name__ == "__main__":
#     push()
#
if __name__ == "__main__":
    register_consumer()
    app.run(host="0.0.0.0", port=5051, threaded=True)
