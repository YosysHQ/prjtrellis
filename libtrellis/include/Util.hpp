#ifndef LIBTRELLIS_UTIL_HPP
#define LIBTRELLIS_UTIL_HPP

#include <string>
#include <sstream>
#include <iomanip>
#include <cstdint>
#include <vector>
#include <boost/range/adaptor/reversed.hpp>
using namespace std;

namespace Trellis {
enum class VerbosityLevel {
    ERROR,
    NOTE,
    DEBUG,
};
extern VerbosityLevel verbosity;

inline string uint32_to_hexstr(uint32_t val) {
    ostringstream os;
    os << "0x" << hex << setw(8) << setfill('0') << val;
    return os.str();
}

inline string to_string(const vector<bool> &bv) {
    ostringstream os;
    for(auto bit : boost::adaptors::reverse(bv))
        os << (bit ? '1' : '0');
    return os.str();
}

}
#define fmt(x) (static_cast<const std::ostringstream&>(std::ostringstream() << x).str())

#endif //LIBTRELLIS_UTIL_HPP
