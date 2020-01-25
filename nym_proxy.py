import asyncio
import base64
import json
import websockets

class NymProxy:

    def __init__(self, port=9001):
        self.uri = "ws://127.0.0.1:%s/mix" % port

    async def __aenter__(self):
        self._ws_handle = websockets.connect(self.uri)
        self.ws = await self._ws_handle.__aenter__()
        return self

    async def __aexit__(self, *args):
        return await self._ws_handle.__aexit__(*args)

    async def request(self, message_type, params={}):
        request_object = {
            "type": message_type,
            **params
        }
        await self.ws.send(json.dumps(request_object))

        response = json.loads(await self.ws.recv())
        return response

    async def details(self):
        response = await self.request("ownDetails")
        address = response["address"]
        return address

    async def clients(self):
        response = await self.request("getClients")
        clients = response["clients"]
        return clients

    async def send(self, message, recipient):
        response = await self.request("send", {
            "message": message,
            "recipient_address": recipient
        })

    async def fetch(self):
        response = await self.request("fetch")
        messages = response["messages"]
        return messages

async def hello():
    async with NymProxy(9002) as nym:
        details = await nym.details()
        print(details)
        clients = await nym.clients()
        print(clients)

def main():
    asyncio.get_event_loop().run_until_complete(hello())

if __name__ == "__main__":
    main()

