from qstash import Receiver
from worker.config import config

receiver = Receiver(
    current_signing_key=config.QSTASH_CURRENT_SIGNING_KEY,
    next_signing_key=config.QSTASH_NEXT_SIGNING_KEY,
)

def verify_signature(body: str, signature: str):
    return receiver.verify({
        "body": body,
        "signature": signature
    })
