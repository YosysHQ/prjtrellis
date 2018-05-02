#include "Bitstream.hpp"
#include "Chip.hpp"
#include <vector>
#include <string>

#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>

using namespace boost::python;
using namespace Trellis;

BOOST_PYTHON_MODULE (pytrellis) {
    class_<vector<string>>("StringVector")
            .def(vector_indexing_suite<vector<string>>());

    class_<vector<uint8_t>>("ByteVector")
            .def(vector_indexing_suite<vector<uint8_t>>());

    class_<Bitstream>("Bitstream", no_init)
            .def("read_bit", &Bitstream::read_bit_py)
            .staticmethod("read_bit")
            .def_readwrite("metadata", &Bitstream::metadata)
            .def_readwrite("data", &Bitstream::data);
}
