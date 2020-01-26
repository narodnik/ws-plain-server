import asyncio
import hashlib
import json
import multipart
import nym_proxy
import sys
import wallet

async def broadcast(tx_data):
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        multi = multipart.Multipart(websocket)

        request = {
            "command": "broadcast",
            "tx_data": tx_data
        }

        await multi.send(request)

        print("Sent.")
        await asyncio.sleep(4)

def main():
    wallet.set_testnet(True)

    if len(sys.argv) != 2:
        print("Usage: broadcast.py TX_DATA")
        return -1

    asyncio.get_event_loop().run_until_complete(broadcast(sys.argv[1]))
    return 0

if __name__ == "__main__":
    sys.exit(main())

