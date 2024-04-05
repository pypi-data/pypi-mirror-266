import json
from abc import ABC

import pika
import uuid

from ai_model_dispatcher.config import AMQP_URL


class BaseDispatcher(ABC):

    def __init__(self):
        self.connection = pika.BlockingConnection(pika.URLParameters(AMQP_URL))
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, model_name, method, payload):
        body = {'method': method, 'payload': payload}
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key=model_name,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=json.dumps(body))
        while self.response is None:
            self.connection.process_data_events(time_limit=0)
        response = json.loads(self.response) if self.response is not None else {}
        return response
