import argparse
import logging
import os
import requests
from dataclasses import asdict
from dataclasses import dataclass
from typing import Any
from typing import Iterable
from dotenv import load_dotenv
from models import MessageRequest
from models import Result
from models import ErrorResult


BASE_URL = "https://graph.microsoft.com/v1.0/"


logger = logging.getLogger(__name__)


load_dotenv()


def get_default_access_token():
    return os.environ.get("TEAMS_ACCESS_TOKEN")


def message_items(message: MessageRequest) -> Iterable[str]:
    if message.title:
        yield f'<h1>{message.title}</h1>'
    if message.text:
        yield f'<p>{message.text}</p>'
    if message.image:
        yield f"<img src='{message.image}'/>"


def compose_message(request: MessageRequest) -> str:
    return ''.join(message_items(request))


def send_message(access_token: str, url: str, message: str) -> Result | ErrorResult:
    logger.info("sending: %s", message)
    headers = { "Authorization": f"Bearer {access_token}" }
    body = { "contentType": "html", "content": message }
    resp =  requests.post(url, headers=headers, json={ "body": body })
    if resp.ok:
        result = resp.json()
        return Result(id=result["id"], url=result["webUrl"])
    else:
        error_body = resp.json()
        logging.error("Status code %s, %s, failed to send message to %s: %s",
                      resp.status_code, error_body, url, { "body": body })
        return ErrorResult(
            status_code=resp.status_code,
            error_message=error_body["error"]["message"]
        )


def channel_message_url(team_id: str, channel_id: str) -> str:
    return f"{BASE_URL}teams/{team_id}/channels/{channel_id}/messages"


def chat_message_url(chat_id: str) -> str:
    return f"{BASE_URL}chats/{chat_id}/messages"


def message_channel(access_token: str, team_id: str, channel_id: str,
                    request: MessageRequest) -> Result | ErrorResult:
    url = channel_message_url(team_id, channel_id)
    message = compose_message(request)
    return send_message(access_token, url, message)


def message_chat(access_token: str, chat_id: str,
                 request: MessageRequest) -> Result | ErrorResult:
    url = chat_message_url(chat_id)
    message = compose_message(request)
    return send_message(access_token, url, message)


if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument("--text")
    parser.add_argument("--title")
    parser.add_argument("--image")
    parser.add_argument("team_id", help="Team ID of the message intends to")
    parser.add_argument("channel_id", help="Channel ID of the message intends to")

    args = parser.parse_args()
    token = get_default_access_token()
    team_id = args.team_id
    channel_id = args.channel_id
    text = args.text
    title = args.title or ""
    image_url = args.image or ""

    if token:
        if team_id and channel_id:
            if text or title or image_url:
                message = MessageRequest(text=text, title=title, image=image_url)
                result = message_channel(token, team_id, channel_id, message)
                print("Messaging result", result)
            else:
                print("Please specify atleast one of --text, --title, --image")
        else:
            print("Team ID and channel ID are required as the first two positional arguments")
    else:
        print("Cannot find access token in environment variable TEAM_ACCESS_TOKEN")
