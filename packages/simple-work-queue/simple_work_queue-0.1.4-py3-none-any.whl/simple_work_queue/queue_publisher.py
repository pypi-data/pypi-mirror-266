"""
QueuePublisher defines a protocol for publishing messages to a queue. It
will have a single method, publish, that takes a message as an argument
and returns a boolean value indicating whether the message was
successfully published. The QueuePublisherSpoolDir and
QueuePublisherPubSub classes will implement this protocol for publishing
messages to a spool directory and a pub/sub queue, respectively.
"""

from typing import Protocol
import os
import uuid


class QueuePublisher(Protocol):
    def publish(self, message: str) -> bool: ...


class QueuePublisherSpoolDir(QueuePublisher):
    def __init__(self, spool_dir: str, file_extension: str = None):
        self.spool_dir = spool_dir
        self.file_extension = file_extension

    def publish(self, message: str) -> bool:
        try:
            if not os.path.exists(self.spool_dir):
                os.makedirs(self.spool_dir)
            request_id = uuid.uuid1()
            with open(
                os.path.join(self.spool_dir, f"{request_id}{self.file_extension}"), "w"
            ) as f:
                f.write(message)
            return True
        except Exception as e:
            print(f"Error publishing message: {e}")
            return False
