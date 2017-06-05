import pika
import random
import json
from pick import pick
import threading

company_names = ['Chicita Bananas', 'Bart Banaan', 'Pink', 'Yellow Fruit', 'Tucan Colombia Inc.', 'Pleb Bv.']
company_name = company_names[random.randint(0, len(company_names) - 1)]
print('Company: %s ' % (company_name))

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel_result = connection.channel()
channel_winner = connection.channel()

channel_result.exchange_declare(exchange='result', type='fanout')

channel.exchange_declare(exchange='orders', type='fanout')
result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue
channel.queue_bind(exchange='orders', queue=queue_name)

channel_winner.exchange_declare(exchange='winner', type='fanout')
result_winner = channel_winner.queue_declare(exclusive=True)
queue_name_winner = result_winner.method.queue
channel_winner.queue_bind(exchange='winner', queue=queue_name_winner)

print(' [*] Waiting for orders. To exit press CTRL+C')


def callback(ch, method, properties, body):
    body = body.decode("utf-8")
    if pick(['yes', 'no'], 'Accept this order?: %s' % body)[0] == 'yes':
        order = json.loads(body)
        order['company-name'] = company_name
        message = json.dumps(order)
        channel_result.basic_publish(exchange='result', routing_key='', body=message)
        print('Sent confirmation to broker: %s' % message)


def callback_winner(ch, method, properties, body):
    print('Order given to: %s' % body)

channel.basic_consume(callback, queue=queue_name, no_ack=True)
channel_winner.basic_consume(callback_winner, queue=queue_name_winner, no_ack=True)


def thread1():
    channel.start_consuming()


def thread2():
    channel_winner.start_consuming()

t1 = threading.Thread(target=thread1, args = ())
t1.daemon = True
t1.start()

t2 = threading.Thread(target=thread2, args = ())
t2.daemon = True
t2.start()

while(True):
    pass
