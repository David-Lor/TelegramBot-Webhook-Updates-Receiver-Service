# Telegram Bot Updates Receiver Service

The objective of this project is to build a microservice that receives updates from a Telegram Bot through Webhook, and publishes them on a message broker or queue system (like MQTT, AMQP, Kafka or Redis), to be consumed by one or more processing microservices.

**This project is currently a Proof of Concept.**

## Architecture

A very basic architecture would involve three services:

- A message broker/queue service
- The Receiver Service (current repository)
- A Consumer Service, that consumes updates and processes them, including all the business logic behind the bot - ending with calls to the Telegram Bot API to send responses to the users

![Architecture diagram](docs/architecture.svg)

## Why

### Advantages

- The Consumer Services can be developed without having to deal with the development and/or implementation of the Webhook updates receiver
- Multiple consumer microservices can be deployed, for redundancy and/or to keep different business logic

### Disadvantages

- Maintaining multiple microservices can be overkill in many use-cases
- If using multiple Consumer Services, synchronization between them must be implemented if required (e.g. for caching data or keeping context of messages received)
- Some libraries do not allow injecting arbitrary Telegram Bot Updates JSON data

## Getting started

The initial PoC consists of the `receiver.py` script, which **currently** works as following:

- For simplicity, is intended to work using [ngrok](https://ngrok.com/) - a free tunnelling service that exposes a local port on a public URL, without opening/forwarding ports in your local network.
- We run Flask to serve the webhook for Telegram Updates, without SSL - by default, ngrok creates a https URL, with a valid certificate, so we do not need to create a self-signed certificate and pass it to Telegram.
  However, the script currently supports creating and using self-signed certificates, but if using ngrok it is required to create a (free) account in order to forward https directly.
- The current PoC only prints received Telegram Bot updates using a logging module - it does not publish them anywhere.

The steps required to make it work are the following (`Lxx` refers to lines in file `receiver.py`):

- Create a bot using BotFather.
- Paste its token in L10 (non-PoC version will use proper settings!).
- Install the Python requirements in [requirements.txt](requirements.txt) (using a virtual environment is recommended).
- Download and start running ngrok with the command: `ngrok http 8080` (the port refers to the Flask server, which can be changed in L12).
- Paste the ngrok domain (which in free accounts would be something like `(bunch of letters and numbers).ngrok.io`) in L11 (do not copy the leading `https://`). Remember that this domain changes each time the ngrok service is started.
- Run the script (`python receiver.py`).

The module works as following (see the `main()` method for reference):

- A self-signed certificate could be generated initially.
- Call the Telegram Bot API endpoint to setup the webhook, using the full URL (if using a self-signed certificate, this will be appended to the API call so Telegram can use it). The webhook token is randomly generated each time the script runs.
- Register the teardown method at exit, which will call the Telegram Bot API endpoint to delete the webhook, when the script stops running.
- Setup the Flask server, by creating an instance of it and registering the endpoints (one status endpoint, and the current webhook endpoint that will receive Telegram Bot updates).
- Start running the Flask server (using the self-signed certificate, if any).

## Settings

Settings are defined using environment variables, or a .env file. Variables defined as environment variables will override those defined in the .env file.

- **General**
  - **ENV_FILE**: (default: `.env`) path of the .env file to load settings from. If the file does not exist or cannot be found, settings will not load from .env file.
- **Webhook**
  - **WEBHOOK_DOMAIN**: (**required**) domain where webhook is served; does not include "https://" nor the endpoint.
  - **WEBHOOK_ENDPOINT**: (default: `random`) endpoint where Telegram will send Webhook POST requests. With the domain, forms the webhook URL that is sent to Telegram to send bot updates to. Can be one of:
    - `random`: generate a random UUID4 string as endpoint, each time the application starts
    - `token`: use the bot token as endpoint
    - any other valid string will be used as-is as endpoint
  - **WEBHOOK_BIND**: (default: `0.0.0.0`) address to host the webhook server on.
  - **WEBHOOK_PORT**: (default: `8000`) port to host the webhook server on.
  - **WEBHOOK_STATUS_ENDPOINT**: (default: `true`) if false, do not serve a `/status` endpoint, accessible from any host to verify that the server is accessible.
  - **WEBHOOK_LIMIT_SUBNETS**: (optional) comma-separated list of networks, with the format `ip/mask`, that can be used for limiting access to the webhook endpoint to hosts from these subnetworks. The subnetworks used by Telegram, as stated [in their documentation](https://core.telegram.org/bots/webhooks), would be `149.154.160.0/20,91.108.4.0/22` (keep in mind that these could change in the future). If not specified, no limitations will be applied.
- **Telegram**
  - **TELEGRAM_TOKEN**: (**required**) Telegram Bot token.
  - **TELEGRAM_DELETE_WEBHOOK**: (default: `true`) if true, delete the webhook when the application closes.
- **Redis**
  - **REDIS_URL**: (optional) if specified, put bot updates on a queue of the given Redis server. URL example: `redis://localhost:6379`.
  - **REDIS_QUEUE_NAME**: (default: `telegram_bot`) name of the Redis queue where bot updates are put.

## TODO

- Integrate with ngrok (auto-load domain from Free plan)
- Allow creating and/or using self-signed certificates

## Changelog

- 0.0.1
    - Initial PoC script
