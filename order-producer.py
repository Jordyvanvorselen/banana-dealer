from question import question
from pick import pick
import pika
import json
import random
from datetime import datetime, timedelta

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel_winner = connection.channel()

channel.exchange_declare(exchange='orders', type='fanout')
channel_winner.exchange_declare(exchange='winner', type='fanout')
result_winner = channel_winner.queue_declare(exclusive=True)
queue_name_winner = result_winner.method.queue
channel_winner.queue_bind(exchange='winner', queue=queue_name_winner)


def callback_winner(ch, method, properties, body):
    print('Order given to: %s' % body)

questions = [
    "What type of banana do you want to order?",
    "How many banana's do you want to order?",
    "At what time do you want the banana's to be delivered?"
]
types = ['Lady Finger', 'Red Bananas', 'Cooking Bananas', 'Normal Bananas']
times = [
    (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
    (datetime.now() + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),
    (datetime.now() + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
    (datetime.now() + timedelta(hours=4)).strftime('%Y-%m-%d %H:%M:%S'),
    (datetime.now() + timedelta(hours=5)).strftime('%Y-%m-%d %H:%M:%S'),
]

message = json.dumps({
    'order-id': random.randint(0, 99999999999),
    'type': pick(types, questions[0])[0],
    'amount': float(question(questions[1])),
    'time': pick(times, questions[2])[0],
})

channel.basic_publish(exchange='orders', routing_key='', body=message)

print(" [x] Sent order %r" % message)

channel_winner.basic_consume(callback_winner, queue=queue_name_winner, no_ack=True)
channel_winner.start_consuming()
