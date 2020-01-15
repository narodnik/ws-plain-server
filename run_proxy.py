import asyncio
import json
import nym_proxy
import wallet

async def process(message, nym):
    print("Processing:", message)

    try:
        message = json.loads(message)
    except json.decoder.JSONDecodeError:
        print("Error decoding message.")

    try:
        addrs = message["addrs"]
        return_recipient = message["return-recipient"]
    except KeyError:
        print("Error reading keys")

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


