# 1. Consume message from RabbitMQ queue
# 2. Convert the message to morse
# 3. Send the message to serial console
# 4. Wait for "DONE" acknowledgement
# 5. Publish "SENT"

import serial, time, pika, os, sys, json, jsonschema
from dotenv import load_dotenv
load_dotenv()

# Run `python -m serial.tools.list_ports` to list the ports

arduino = serial.Serial(port=os.getenv('SERIAL_PORT','COM3'),baudrate=os.getenv('BAUD_RATE',9600))
time.sleep(2)

character_morse_map = {
    # Letters
    'a': '.-',     'b': '-...',   'c': '-.-.',   'd': '-..',
    'e': '.',      'f': '..-.',   'g': '--.',    'h': '....',
    'i': '..',     'j': '.---',   'k': '-.-',    'l': '.-..',
    'm': '--',     'n': '-.',     'o': '---',    'p': '.--.',
    'q': '--.-',   'r': '.-.',    's': '...',    't': '-',
    'u': '..-',    'v': '...-',   'w': '.--',    'x': '-..-',
    'y': '-.--',   'z': '--..',

    # Digits
    '0': '-----',  '1': '.----',  '2': '..---',  '3': '...--',
    '4': '....-',  '5': '.....',  '6': '-....',  '7': '--...',
    '8': '---..',  '9': '----.',

    # Punctuation
    '.': '.-.-.-', ',': '--..--', '?': '..--..', "'": '.----.',
    '!': '-.-.--', '/': '-..-.',  '(': '-.--.',  ')': '-.--.-',
    '&': '.-...',  ':': '---...', ';': '-.-.-.', '=': '-...-',
    '+': '.-.-.',  '-': '-....-', '_': '..--.-', '"': '.-..-.',
    '$': '...-..-', '@': '.--.-.',

    # Word Space
    ' ': ' '
}

payload_schema = {
    "type" : "object",
    "properties" : {
        "id" : {"type" : "number"},
        "user_id" : {"type" : "number"},
        "message" : {"type" : "string"}
    },
}

def encode_morse(message: str):
    if len(message) > 0:
        encoded_message = ""
        words = message.split(' ')
        for word in words:
            encoded_word = ""
            for c in word:
                if c == ' ':
                    encoded_word = encoded_word + ' '
                else:
                    encoded_word = encoded_word + character_morse_map.get(c) + '_'
            encoded_message = encoded_message + encoded_word.strip('_') + ' '
        return encoded_message.strip()
    else:
        return None

def decode_morse(encoded_message: str):
    if len(encoded_message) > 0:
        decoded_message = ""
        encoded_words = encoded_message.split(' ')
        print(encoded_words)
        for encoded_word in encoded_words:
            encoded_letters = encoded_word.split('_')
            print(encoded_letters)
            for encoded_letter in encoded_letters:
                print(encoded_letter)
                decoded_message = decoded_message + (list(character_morse_map.keys())[list(character_morse_map.values()).index(encoded_letter)])
            decoded_message = decoded_message + ' '
        return decoded_message.upper()
    else:
        return None

def send_encoded_message(encoded_message: str):
    arduino.write(bytes(encoded_message, 'utf-8'))
    data = arduino.readline()
    return data.decode('utf-8')

def parse_payload(payload: any):
    utf_decoded_payload = str(payload.decode('utf-8'))
    parsed_payload = json.loads(utf_decoded_payload)
    # clean_payload = utf_decoded_payload.replace('\r', '').replace('\n', ' ').lower()
    return parsed_payload

def is_valid_payload(payload: any):
    try:
        jsonschema.validate(payload, payload_schema)
        return True
    except Exception as e:
        print(e)
        return False


def main():
    credentials = pika.PlainCredentials(username=os.getenv('RMQ_USER'), password=os.getenv('RMQ_PASSWORD'))
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost',port=5672, credentials=credentials))
    channel = connection.channel()

    channel.queue_declare(queue='message.q', durable=True, arguments={'x-queue-type': 'quorum'})

    def process_payload(ch, method, properties, body):
        parsed_payload = parse_payload(body)
        print(parsed_payload)
        if is_valid_payload(parsed_payload):
            message = parse_payload['message']
            print(f" [x] Message: {message}")
            morse_encoded_message = encode_morse(message)
            print(f" [x] Encoded message: {morse_encoded_message}")
            send_encoded_message(morse_encoded_message)
            print(' [x] Message sent successfully.')
        else:
            print(' [x] ERROR: Invalid payload.')


    channel.basic_consume(queue='message.q', on_message_callback=process_payload, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)