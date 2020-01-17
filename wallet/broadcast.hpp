#ifndef BIJIWALLET_BROADCAST_HPP
#define BIJIWALLET_BROADCAST_HPP

#include <pybind11/pybind11.h>
namespace py = pybind11;

void broadcast(const py::bytes& tx_data);

#endif // BIJIWALLET_BROADCAST_HPP

