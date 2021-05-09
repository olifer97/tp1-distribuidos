from hashlib import sha256
import json
import datetime

from constants import *


class Block:
    def __init__(self, prev_hash, difficulty, chunks):
        self.chunks = chunks
        self.header = {
            "prev_hash": prev_hash,
            "difficulty": difficulty,
            "nonce": 0,
            "entries_amount": len(chunks),
        }

    def setTimestamp(self, timestamp):
        self.header["timestamp"] = timestamp

    def addNonce(self):
        self.header["nonce"] += 1

    def hash(self):
        return int(sha256(str(self.header).encode('utf-8') + str(self.chunks).encode('utf-8')).hexdigest(), 16)

    def difficulty(self):
        return self.header["difficulty"]

    def serialize(self):
        return json.dumps(self.asDict())

    def asDict(self):
        copy_header = self.header
        copy_header["timestamp"] = copy_header["timestamp"].strftime(TIMESTAMP_FORMAT)
        return {"chunks": self.chunks, "header": copy_header}

    def prevHash(self):
        return self.header['prev_hash']

    @classmethod
    def deserialize(cls, data):
        json_data = json.loads(data)
        block = cls(json_data["header"]["prev_hash"],
                    json_data["header"]["difficulty"], json_data["chunks"])
        block.header["nonce"] = json_data["header"]["nonce"]
        block.header["timestamp"] = datetime.datetime.strptime(json_data["header"]["timestamp"], TIMESTAMP_FORMAT)

        return block
