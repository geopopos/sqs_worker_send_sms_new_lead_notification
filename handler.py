import json
import logging
import os

import boto3

from twilio.rest import Client


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

QUEUE_URL = os.getenv('QUEUE_URL')
SQS = boto3.client('sqs')


def producer(event, context):
    print(event.get('body'))
    status_code = 200
    message = ''

    if not event.get('body'):
        return {'statusCode': 400, 'body': json.dumps({'message': 'No body was found'})}

    try:
        message_attrs = {
            'AttributeName': {'StringValue': 'AttributeValue', 'DataType': 'String'}
        }
        SQS.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=event['body'],
            MessageAttributes=message_attrs,
        )
        message = 'Message accepted!'
    except Exception as e:
        logger.exception('Sending message to SQS queue failed!')
        message = str(e)
        status_code = 500

    return {'statusCode': status_code, 'body': json.dumps({'message': message})}


def consumer(event, context):
    # set twilio account sid and auth token
    logger.info('Received message: {}'.format(event))
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    # grab message body and number to send message to
    event_body = json.loads(event.get('Records')[0].get('body'))
    message_body = event_body.get('message_body')
    to_number = event_body.get('to_number')
    if not to_number and not message_body:
        return {'statusCode': 400, 'body': json.dumps({'message': 'sms request requires a message_body and to_number field'})}

    logger.info(f"MESSAGE BODY :==> {message_body}")
    logger.info(f"TO NUMBER:==> {to_number}")


    message = client.messages.create(
                     body=message_body,
                     from_='+14439032242',
                     to=to_number
                 )

    logger.info(message.sid)
    