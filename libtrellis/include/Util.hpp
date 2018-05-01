#ifndef LIBTRELLIS_UTIL_HPP
#define LIBTRELLIS_UTIL_HPP

#include <string>
#include <sstream>
#include <iomanip>
#include <cstdint>

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

}

#endif //LIBTRELLIS_UTIL_HPP
