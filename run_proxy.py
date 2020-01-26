import asyncio
import hashlib
import json
import multipart
import wallet
import websockets

async def process(message, multi):
    print("Processing:", message)

    try:
        command = message["command"]
    except KeyError:
        print("Error reading keys")
        return

    if command == "fetch_history":
        await fetch_history(message, multi)
    elif command == "broadcast":
        await broadcast(message, multi)
    else:
        print("Unknown command:", command)

async def fetch_history(message, multi):
    try:
        addrs = message["addrs"]
        return_recipient = message["return-recipient"]
    except KeyError:
        print("Error reading fetch_history keys")
        return

    print("Fetching history for:", addrs)
    histories = wallet.fetch_history(addrs)
    print("Histories fetched. Continuing...")

    histories_json = {}
    for address, history in histories.items():
        address_json = []
        for row in history:
            # Add the output
            address_json.append(
                ("output", row.output.hash.hex(), row.output.index,
                 row.output.height, row.value))

            if row.spend is not None:
                address_json.append(
                    ("spend", row.spend.hash.hex(), row.spend.index,
                     row.spend.height, -row.value))
        histories_json[address] = address_json

    await multi.send(histories_json)

transactions = {}

def tx_hash(tx_data):
    sha256 = lambda data: hashlib.sha256(data).digest()
    return sha256(sha256(tx_data))[::-1].hex()

async def broadcast(message, multi):
    try:
        tx_data = message["tx_data"]
    except KeyError:
        print("Error reading tx_data")
        return

    try:
        tx = bytes.fromhex(tx_data)
    except ValueError:
        print("Error reading hex data from tx")
        return

    print("Broadcasting tx = ", tx_hash(tx))
    wallet.broadcast(tx)

async def accept(websocket, path):
    multi = multipart.Multipart(websocket)

    while True:
        try:
            message = await multi.receive()
            await process(message, multi)
        except websockets.exceptions.ConnectionClosedOK:
            print("Websocket closed. Exiting...")
            return

        await asyncio.sleep(0.1)

def main():
    wallet.set_testnet(True)

    start_server = websockets.serve(accept, "localhost", 8765)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()

