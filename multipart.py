import asyncio
import hashlib
import json
import nym_proxy
import random

def compute_id(data):
    sha256 = lambda data: hashlib.sha256(data).digest()
    return sha256(sha256(data.encode()))[::-1].hex()

class Multipart:

    def __init__(self, nym):
        self.nym = nym

        self._parts = {}

    async def send(self, message, recipient, size_limit=500):
        data = json.dumps(message)

        split_string = lambda string, chunk_size: \
            [string[i:i + chunk_size]
             for i in range(0, len(string), chunk_size)]
        chunks = split_string(data, size_limit)

        data_id = compute_id(data)

        #print("Sending:", chunks)
        #print("ID:", data_id)

        chunks = list(enumerate(chunks))
        random.shuffle(chunks)

        for i, chunk in chunks:
            message = {
                "id": data_id,
                "payload": chunk,
                "index": i
            }
            await self.nym.send(json.dumps(message), recipient)

    async def receive(self):
        while True:
            messages = await self.nym.fetch()
            
            for message in messages:
                result = self._process(message)
                if result is not None:
                    return result

            await asyncio.sleep(0.1)

    def _process(self, message):
        message = json.loads(message)

        data_id = message["id"]
        payload = message["payload"]
        index = message["index"]

        if data_id not in self._parts:
            self._parts[data_id] = []

        self._parts[data_id].insert(index, payload)

        combined_payload = "".join(self._parts[data_id])
        
        if compute_id(combined_payload) != data_id:
            return None

        del self._parts[data_id]

        try:
            return json.loads(combined_payload)
        except json.decoder.JSONDecodeError:
            return None

async def client():
    recipient = "kauuj71-RPvETjz8FMQugnsNSDJ8033E4lNS_anMFD0="
    async with nym_proxy.NymProxy(9001) as nym:
        multipart = Multipart(nym)
        message = ["hello world"]
        print("Sending:", message)
        await multipart.send(message, recipient, 5)

async def server():
    async with nym_proxy.NymProxy(9002) as nym:
        #print("Server:", await nym.details())
        multipart = Multipart(nym)
        message = await multipart.receive()
        print("Received:", message)

def main():
    asyncio.get_event_loop().run_until_complete(asyncio.gather(
        client(), server()))

if __name__ == "__main__":
    main()
