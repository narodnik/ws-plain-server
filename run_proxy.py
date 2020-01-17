import asyncio
import hashlib
import json
import nym_proxy
import wallet

async def process(message, nym):
    print("Processing:", message)

    try:
        message = json.loads(message)
    except json.decoder.JSONDecodeError:
        print("Error decoding message.")
        return

    try:
        command = message["command"]
    except KeyError:
        print("Error reading keys")
        return

    if command == "fetch_history":
        await fetch_history(message, nym)
    elif command == "broadcast":
        await broadcast(message, nym)
    else:
        print("Unknown command:", command)

async def fetch_history(message, nym):
    try:
        addrs = message["addrs"]
        return_recipient = message["return-recipient"]
    except KeyError:
        print("Error reading fetch_history keys")
        return

    histories = wallet.fetch_history(addrs)

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

    histories_json_data = json.dumps(histories_json)
    await nym.send(histories_json_data, return_recipient)

transactions = {}

def tx_hash(tx_data):
    tx_data_bytes = bytes.fromhex(tx_data)
    sha256 = lambda data: hashlib.sha256(data).digest()
    return sha256(sha256(tx_data_bytes))[::-1].hex()

async def broadcast(message, nym):
    try:
        tx_chunk = message["tx_chunk"]
        ident = message["id"]
        index = message["index"]
        total = message["total"]
    except KeyError:
        print("Error reading addrs")
        return

    if ident not in transactions:
        transactions[ident] = []

    transactions[ident].insert(index, tx_chunk)

    if len(transactions[ident]) != total:
        print("Buffering chunk.")
        return

    tx_data = "".join(transactions[ident])
    del transactions[ident]

    if tx_hash(tx_data) != ident:
        print("Error sanity check failed")
        return

    try:
        tx = bytes.fromhex(tx_data)
    except ValueError:
        print("Error reading hex data from tx")
        return

    print("Broadcasting tx = ", tx.hex())
    wallet.broadcast(tx)

async def accept():
    async with nym_proxy.NymProxy(9002) as nym:
        print("Server address =", await nym.details())

        while True:
            messages = await nym.fetch()

            if messages:
                [await process(message, nym) for message in messages]

            await asyncio.sleep(0.1)

def main():
    wallet.set_testnet(True)
    asyncio.get_event_loop().run_until_complete(accept())

if __name__ == "__main__":
    main()


