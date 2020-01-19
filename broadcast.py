import asyncio
import hashlib
import json
import multipart
import nym_proxy
import sys
import wallet

async def broadcast(tx_data):
    async with nym_proxy.NymProxy(9001) as nym:
        multi = multipart.Multipart(nym)

        request = {
            "command": "broadcast",
            "tx_data": tx_data
        }

        nym_server_address = "kauuj71-RPvETjz8FMQugnsNSDJ8033E4lNS_anMFD0="
        await multi.send(request, nym_server_address)

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

