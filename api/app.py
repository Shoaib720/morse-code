# 1. Expose 2 endpoints: 
#    i. POST /messages
#    ii. ...
# 2. Configure RMQ connection
# 3. Func to send message to RMQ
# 4. 

from fastapi import FastAPI
from dotenv import load_dotenv
import json, os
import pika

from .models import Message

load_dotenv()

app = FastAPI()

credentials = pika.PlainCredentials(
    username=os.getenv("RMQ_USER"),
    password=os.getenv("RMQ_PASSWORD")
)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=os.getenv('RMQ_HOSTNAME', 'localhost'),
        port=os.getenv('RMQ_PORT', 5672),
        credentials=credentials
    )
)

channel = connection.channel()

QUEUE_NAME = 'messages.q'

channel.queue_declare(queue=QUEUE_NAME, durable=True, arguments={'x-queue-type': 'quorum'})

def publish_message_to_rabbitmq(message: Message):
    serialized_msg = message.model_dump_json()
    print(serialized_msg)
    channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=serialized_msg)
    print('Message queued successfully')

@app.get("/health")
def read_root():
    return {"status": "healthy"}

@app.post("/messages")
def post_message(message: Message):
    publish_message_to_rabbitmq(message)
    return {
        "status": "success"
    }