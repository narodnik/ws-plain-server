#include "broadcast.hpp"

#include <atomic>
#include <iostream>
#include <bitcoin/client.hpp>
#include "config.hpp"

namespace bcs = bc;
namespace bcc = bc::client;

void broadcast(const py::bytes& tx_data)
{
    const std::string tx_data_cast = tx_data;
    const auto data = reinterpret_cast<const uint8_t*>(tx_data_cast.data());
    const bc::data_chunk tx_data_converted(data, data + tx_data_cast.size());

    bc::chain::transaction tx;
    tx.from_data(tx_data_converted);

    if (!tx.is_valid())
    {
        std::cerr << "Error invalid transaction data." << std::endl;
        return;
    }

    std::cout << std::endl;
    std::cout << "Sending: " << bcs::encode_base16(tx.to_data()) << std::endl;
    std::cout << std::endl;

    // Bound parameters.
    bcc::obelisk_client client(4000, 0);

    std::cout << "Connecting to " << biji::blockchain_server_address
        << "..." << std::endl;
    const auto endpoint = bcs::config::endpoint(biji::blockchain_server_address);

    if (!client.connect(endpoint))
    {
        std::cerr << "Cannot connect to server" << std::endl;
        return;
    }

    std::atomic<bool> is_error = false;

    auto on_error = [&is_error](const bcs::code& code)
    {
        std::cout << "error: " << code.message() << std::endl;
        is_error = true;
    };

    auto on_done = [](const bcs::code&)
    {
        std::cout << "Broadcasted." << std::endl;
    };

    // This validates the tx, submits it to local tx pool, and notifies peers.
    client.transaction_pool_broadcast(on_error, on_done, tx);
    client.wait();
}

