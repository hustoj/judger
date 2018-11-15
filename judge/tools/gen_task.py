import json
import toml
import pika
import requests


def publish(cfg):
    credentials = pika.PlainCredentials(cfg['username'], cfg['password'])
    parameters = pika.ConnectionParameters(host=cfg['host'], port=cfg['port'], credentials=credentials)

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.queue_declare(queue='task_queue', durable=True)

    response = requests.get('http://neo.test/judge/api/task')

    channel.basic_publish(exchange='',
                          routing_key='task_queue',
                          body=response.content,
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # make message persistent
                          ))
    print(" [x] Sent %r" % response)
    connection.close()


if __name__ == '__main__':
    cfg = toml.load('../../judge.toml')
    publish(cfg['mq'])