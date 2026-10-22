from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from os import getenv
from pydantic import BaseModel
from pika import PlainCredentials, BlockingConnection, ConnectionParameters

load_dotenv()

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class Message(BaseModel):
    message: str

credentials = PlainCredentials(
    username=getenv("RMQ_USER"),
    password=getenv("RMQ_PASSWORD")
)

connection = BlockingConnection(
    ConnectionParameters(
        host=getenv('RMQ_HOSTNAME', 'localhost'),
        port=getenv('RMQ_PORT', 5672),
        credentials=credentials
    )
)

channel = connection.channel()

QUEUE_NAME = 'message.q'

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