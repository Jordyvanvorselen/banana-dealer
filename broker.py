import pika
import json

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel_result = connection.channel()
channel = connection.channel()

channel_result.exchange_declare(exchange='result', type='fanout')
channel.exchange_declare(exchange='winner', type='fanout')

result = channel_result.queue_declare(exclusive=True)
queue_name = result.method.queue

channel_result.queue_bind(exchange='result', queue=queue_name)

print(' [*] Waiting for orders. To exit press CTRL+C')
order_confirmations = []


def callback(ch, method, properties, body):
    body = json.loads(body)
    if body['order-id'] not in order_confirmations:
        order_confirmations.append(body['order-id'])
        message = json.dumps({body['order-id']: body['company-name']})
        channel_result.basic_publish(exchange='winner', routing_key='', body=message)
        print(message)

channel_result.basic_consume(callback, queue=queue_name, no_ack=True)

channel_result.start_consuming()
