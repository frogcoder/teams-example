import logging
import os
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import status
from models import ErrorResult
from models import MessageRequest
from models import Result
import teams


logging.basicConfig(level=logging.DEBUG)


load_dotenv()


app = FastAPI()


def parse_result(result: Result | ErrorResult) -> Result:
    match result:
        case Result():
            return result
        case ErrorResult(status_code=status.HTTP_404_NOT_FOUND, error_message=detail):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
        case ErrorResult(error_message=detail):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


@app.post("/teams/{team_id}/channels/{channel_id}/messages",
          status_code=status.HTTP_201_CREATED)
def send_channel_message(team_id: str, channel_id: str, message: MessageRequest) -> Result:
    token = teams.get_default_access_token()
    result = teams.message_channel(token, team_id, channel_id, message)
    return parse_result(result)


@app.post("/chats/{chat_id}/messages", status_code=status.HTTP_201_CREATED)
def send_chat_message(chat_id: str, message: MessageRequest) -> Result:
    token = teams.get_default_access_token()
    result = teams.message_chat(token, chat_id, message)
    return parse_result(result)
