import json
import numpy as np

from block2 import Block


class BlockChainEncoder(json.JSONEncoder):
    def default(self, obj):
        # If the object is a Block, convert it to a dictionary
        if isinstance(obj, Block):
            data = {
                "block_number": obj.block_number,
                "transactions": obj.transactions,
                "previous_hash": obj.previous_hash,
                "nonce": obj.nonce,
                "hashid": obj.hashid,
                # If the object has a datetime attribute, convert it to a string
                "timestamp": obj.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
            # Check if the transactions value is a dictionary or not
            if isinstance(data["transactions"], dict):
                # Loop through the transactions dictionary and convert any numpy arrays to lists
                for key, value in data["transactions"].items():
                    if isinstance(value, np.ndarray):
                        data["transactions"][key] = value.tolist()
            print(data)
            return data
        # If the object is not a Block, use the default JSONEncoder method
        return json.JSONEncoder.default(self, obj)
