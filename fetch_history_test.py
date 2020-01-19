import asyncio
import json
import multipart
import nym_proxy
import wallet

def display_history(histories):
    for address, history in histories.items():
        for row_type, output_hash, output_index, height, value in history:
            value_string = wallet.encode_base10(value)

            print("row_type=%s hash=%s index=%s height=%s value=%s" %
                  (row_type, output_hash, output_index, height, value_string))

async def fetch():
    # WIF private keys
    keys = [
        "cVks5KCc8BBVhWnTJSLjr5odLbNrWK9UY4KprciJJ9dqiDBenhzr"
    ]

    # Convert them to addresses
    addrs = [wallet.key_to_address(key) for key in keys]
    print("Our addresses:", addrs)

    async with nym_proxy.NymProxy(9001) as nym:
        nym_address = await nym.details()

        multi = multipart.Multipart(nym)

        blockchain_request = {
            "command": "fetch_history",
            "addrs": addrs,
            "return-recipient": nym_address
        }
        print("Sending:", blockchain_request)

        nym_server_address = "kauuj71-RPvETjz8FMQugnsNSDJ8033E4lNS_anMFD0="
        await multi.send(blockchain_request, nym_server_address)

        history = await multi.receive()
        display_history(history)

def main():
    wallet.set_testnet(True)
    asyncio.get_event_loop().run_until_complete(fetch())

if __name__ == "__main__":
    main()

