import os

AMQP_URL = os.getenv('AMQP_URL', 'amqp://app:app@localhost:5672/')
