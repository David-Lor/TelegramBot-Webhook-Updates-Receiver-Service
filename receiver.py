import json
import atexit
import subprocess
from uuid import uuid4
from typing import Optional, Tuple

import requests
import flask
from loguru import logger

TOKEN = ""  # bot token
DOMAIN = ""  # public domain/ip (without https nor port nor endpoint)
SERVER_PORT = 8080


def get_uuid():
    return str(uuid4())


URL_TOKEN = get_uuid()  # random endpoint that Telegram will use for webhook
URL = f"https://{DOMAIN}/{URL_TOKEN}"  # full url with endpoint that Telegram will use for webhook


def generate_certificate() -> Tuple[str, str]:
    """Generate a self-signed certificate. Return the filenames of the (certificate, key).
    Telegram docs about generating self-signed cert: https://core.telegram.org/bots/self-signed
    """
    key_filename = "cert.key"
    certificate_filename = "cert.pem"

    command = ["openssl", "req", "-x509", "-newkey", "rsa:4096", "-sha256", "-nodes", "-days", "365",
               "-subj", f"/C=US/ST=New York/L=Brooklyn/O=Example Brooklyn Company/CN={DOMAIN}",
               "-keyout", key_filename, "-out", certificate_filename]
    logger.debug(f"Generating certificate with command {' '.join(command)}")
    subprocess.check_output(command)

    return certificate_filename, key_filename


def setup_webhook(cert_public_key_filename: Optional[str]):
    """Setup the webhook.
    API reference: https://core.telegram.org/bots/api#setwebhook
    """
    logger.info("Setting webhook setup...")
    cert_file = open(cert_public_key_filename, "rb") if cert_public_key_filename else None

    try:
        body = dict(url=URL)

        files = None
        if cert_file:
            files = dict(certificate=("cert.pem", cert_file))

        r = requests.post(f"https://api.telegram.org/bot{TOKEN}/setWebhook", json=body, files=files)
        r.raise_for_status()
        logger.debug(f"Webhook set with statuscode={r.status_code} body={r.text}")

    finally:
        if cert_file:
            cert_file.close()


def teardown_webhook():
    """Teardown the webhook.
    API reference: https://core.telegram.org/bots/api#deletewebhook
    """
    logger.info("Setting webhook teardown...")

    r = requests.post(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
    r.raise_for_status()
    logger.debug(f"Webhook deleted with statuscode={r.status_code} body={r.text}")


def setup_server() -> flask.Flask:
    """Initialization of a Flask instance and endpoints."""
    app = flask.Flask(__name__)
    response_ok = lambda: flask.make_response(flask.jsonify(result=True), 200)

    @app.route("/status", methods=["GET", "POST"])
    def status_endpoint():
        return response_ok()

    @app.route(f"/{URL_TOKEN}", methods=["POST"])
    def telegram_entrypoint():
        body = flask.request.get_json(force=True)
        logger.info(f"Received update: {json.dumps(body)}")
        return response_ok()

    return app


def run_server(app: flask.Flask, certificate_filename: Optional[str], key_filename: Optional[str]):
    """Start running the given Flask app instance in foreground."""
    ssl_context = None
    if certificate_filename and key_filename:
        ssl_context = (certificate_filename, key_filename)

    app.run(ssl_context=ssl_context, host="0.0.0.0", port=SERVER_PORT)


def main():
    # cert_certificate_filename, cert_key_filename = generate_certificate()
    cert_certificate_filename, cert_key_filename = None, None  # using ngrok
    setup_webhook(cert_certificate_filename)
    atexit.register(teardown_webhook)

    server = setup_server()
    run_server(app=server, certificate_filename=cert_certificate_filename, key_filename=cert_key_filename)


if __name__ == "__main__":
    main()
