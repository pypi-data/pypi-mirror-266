import pika
import json

from .configurations import Configuration, Configurable

class RabbitService(Configurable):
    def __init__(self, config: Configuration) -> None:
        Configurable.__init__(self, config)
        self.host = self.config.get_value("rabbit:host")
        self.username = self.config.get_value("rabbit:credentials:username")
        self.password = self.config.get_value("rabbit:credentials:password")

    def get_rabbit_parameters(self):
        return self.host, self.username, self.password

    def enqueue(self, queue_name:str, data):
        host, user, password = self.get_rabbit_parameters()
        creds = pika.PlainCredentials(user, password)
        with pika.BlockingConnection(pika.ConnectionParameters(host, credentials=creds)) as c:
            channel = c.channel()
            channel.queue_declare(queue_name, durable=True, auto_delete=False)
            channel.basic_publish(exchange='', routing_key=queue_name, body=json.dumps(data, indent='\t'))
            c.close()

    def dequeue(self, queue_name:str):
        host, user, password = self.get_rabbit_parameters()
        creds = pika.PlainCredentials(user, password)
        with pika.BlockingConnection(pika.ConnectionParameters(host, credentials=creds)) as c:
            channel = c.channel()
            channel.queue_declare(queue_name, durable=True, auto_delete=False)
            method, properties, body = channel.basic_get(queue_name, True)
            c.close()
            return json.loads(body) if body else None
