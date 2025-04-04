import logging
import json
import os
from typing import Any
from typing import Optional
from dotenv import load_dotenv
from confluent_kafka import Consumer
import teams
from models import MessageRequest


logging.basicConfig(level=logging.DEBUG)


load_dotenv()


logger = logging.getLogger(__name__)


def get_configuration():
    servers = os.environ.get("KAFKA_SERVERS")
    group_id = os.environ.get("KAFKA_GROUP_ID")
    if (username := os.environ.get("KAFKA_USERNAME")):
        # if username is available it is assumed using SASL_SSL security protocol
        return {'bootstrap.servers': servers,
                'sasl.username': username,
                'sasl.password': os.environ.get("KAFKA_PASSWORD"),
                'group.id': group_id,
                'security.protocol': 'SASL_SSL',
                'sasl.mechanism': 'PLAIN',
                'auto.offset.reset': 'smallest'}
    else:
        return {'bootstrap.servers': servers,
                'group.id': group_id,
                'auto.offset.reset': 'smallest'}


def message_request_from_dict(source_dict: dict[str, Any]):
    return MessageRequest(
        text = source_dict.get("text"),
        title = source_dict.get("title"),
        image = source_dict.get("image")
    )

def process_message_channel(source: str):
    logger.info("Message: %s", source)
    try:
        source_dict = json.loads(source)
        team_id = source_dict.get("teamId")
        channel_id = source_dict.get("channelId")
        request = message_request_from_dict(source_dict)
        token = teams.get_default_access_token()
        teams.message_channel(token, team_id, channel_id, request)
    except:
        logger.exception("Error process channel message")


def process_message_chat(source: str):
    logger.info("Message: %s", source)
    try:
        source_dict = json.loads(source)
        chat_id = source_dict.get("chatId")
        request = message_request_from_dict(source_dict)
        token = teams.get_default_access_token()
        teams.message_chat(token, chat_id, request)
    except:
        logger.exception("Error processing chat message")


def consume_loop(consumer: Consumer, channel_topic: Optional[str], chat_topic: Optional[str]):
    topics = [t for t in [channel_topic, chat_topic] if t]
    try:
        logger.info("Topics", topics)
        consumer.subscribe(topics)
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg:
                if msg.error():
                    logger.error("Error when consuming message: %s", msg.error())
                elif msg.topic() == channel_topic:
                    process_message_channel(msg.value().decode("utf-8"))
                else:
                    process_message_chat(msg.value().decode("utf-8"))
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()


config = get_configuration()

channel_topic = os.environ.get("KAFKA_CHANNEL_TOPIC")
chat_topic = os.environ.get("KAFKA_CHAT_TOPIC")
if channel_topic or chat_topic:
    consumer = Consumer(config)
    consume_loop(consumer, channel_topic, chat_topic)
else:
    print("No topic provided")
