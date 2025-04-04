# teams-example
An example API service that send messages to Microsoft Teams and a Kafka consume does the same task.

## Setup
1. `cd` to the project directory.
2. Create virtual environment
```bash
python -mvenv .
```
3. Install the dependencies
```bash
pip install .
```

## Start the API Server
The API server is built upon `FastAPI`, to start the server, in the `src` directory type
```bash
fastapi dev ./api_server.py
```

## Making request to the API Server
`doc/api_server.html` contains the API document.  The document can also be retrieve from the service when it is runing.  The document URL path is `/doc` or `/redoc`.  For example `http://localhost:8000/doc`.

### Environment Variables
For testing, you can edit `.env` file to simulate environment variable.
The API server needs only one envrionment variable `TEAMS_ACCESS_TOKEN` which is the access token to acquire prior sending the messages.

### Sending a Message to Teams Channel
Sending a message require `POST` to the channel message URL with header `Content-Type: application/json`.
The url path for sending to Teams channel contains two variable that are requeired.  The `team_id` and `channel_id`.  An example `http://localhost:8000/teams/{team_id}/channels/{chanel_id}/messages`.
The request body contains a `JSON` object which can contain up to three fields, at least one of the field is required.  The fields are `text`, `title`, `image`.  The `image` is an URL to an image.
An example
```json
{
  "text": "Hello",
  "title": "API Message",
  "image": "https://uhf.microsoft.com/images/microsoft/RE1Mu3b.png"
}
```

### Sending a Message to Teams Chat
The only difference between sending a mesage to chat and to channel is the URL path which takes only one variable `chat_id`.  An example `http://localhost:8000/chats/{chat_id}/messages`.


## Start the Kafka Consumer
In the `src` directory type
```bash
python ./consume_message.py
```
## Environment Variables for Kafka Consumer
A few environment variable need to be set for the Kafka consumer.
* KAFKA_GROUP_ID

  The group ID that the consumer belongs.

* KAFKA_CHANNEL_TOPIC

  The topic that is for sending messages to Teams channels.
  
* KAFKA_CHAT_TOPIC

  The topic that is for sending messages to chats.

* KAFKA_USERNAME

  If the is set, the security protocol of `SASL_SSL` is assumed.  If not set, the consumer will try to connect without username and password.

* KAFKA_PASSWORD

  The password for connecting to Kafka server.  If `KAFKA_USERNAME` is not set, this variable will be ignored.

* KAFKA_SERVERS

  The server names and port to connect to.

## Channel messages to Kafka
The value of the Kafka event should contain a `JSON` object with the following fields.
```json
{
  "teamId": "bb31fc8a-0c56-45cc-aca2-fb3c3a9ca82d",
  "channelId": "19:eaf4f5a3a53449b7b01d723c5bf8fc58@thread.tacv2",
  "text": "Kafka message",
  "title": "A Message Title",
  "image": "https://uhf.microsoft.com/images/microsoft/RE1Mu3b.png"
}
```
## Chat message to Kafka
The only difference between sending a chat message and a channel message is that `chatId` is needed, and `teamId` and `channelId` are not needed.
