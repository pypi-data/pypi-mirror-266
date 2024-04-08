"""QueueConsumer defines a protocol for consuming messages from a queue."""

from typing import Protocol
import os
from time import sleep


class QueueConsumer(Protocol):
    def consume_forever(self, process_request_func: bool, max_iterations=0) -> None: ...


class QueueConsumerSpoolDir(QueueConsumer):
    def __init__(self, spool_dir: str, file_extension: str = None):
        self.spool_dir = spool_dir
        self.file_extension = file_extension

    def consume_forever(self, process_request_func: bool, max_iterations=0) -> None:
        iterations = 0
        keep_going = True
        while keep_going:
            files = list()
            if self.file_extension is not None:
                files = [
                    filename
                    for filename in os.listdir(self.spool_dir)
                    if filename.endswith(self.file_extension)
                ]
            else:
                files = os.listdir(self.spool_dir)
            file = files.pop()
            if file is not None:
                try:
                    with open(os.path.join(self.spool_dir, file), "r") as f:
                        message = f.read()
                    result = process_request_func(message)
                    if result:
                        os.remove(os.path.join(self.spool_dir, file))
                except Exception as e:
                    print(f"Error processing file {file}: {e}")
            else:
                sleep(1)
            iterations += 1
            if (max_iterations > 0) and (iterations >= max_iterations):
                keep_going = False
