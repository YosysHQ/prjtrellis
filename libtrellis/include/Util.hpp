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
    for (auto bit : boost::adaptors::reverse(bv))
        os << (bit ? '1' : '0');
    return os.str();
}

inline istream &operator>>(istream &in, vector<bool> &bv) {
    bv.clear();
    string s;
    in >> s;
    for (auto c : boost::adaptors::reverse(s)) {
        assert((c == '0') || (c == '1'));
        bv.push_back((c == '1'));
    }
    return in;
}

// Skip whitespace, optionally including newlines
inline void skip_blank(istream &in, bool nl = false) {
    int c = in.peek();
    while (in && (((c == ' ') || (c == '\t')) || (nl && ((c == '\n') || (c == '\r'))))) {
        in.get();
        c = in.peek();
    }
}
// Return true if end of line (or file)
inline bool skip_check_eol(istream &in) {
    skip_blank(in, false);
    if (!in)
        return false;
    int c = in.peek();
    // Comments count as end of line
    if (c == '#') {
        in.get();
        c = in.peek();
        while (in && c != EOF && c != '\n') {
            in.get();
            c = in.peek();
        }
        return true;
    }
    return (c == EOF || c == '\n');
}


// Skip past blank lines and comments
inline void skip(istream &in) {
    skip_blank(in, true);
    while (in && (in.peek() == '#')) {
        // Skip comment line
        skip_check_eol(in);
        skip_blank(in, true);
    }
}

// Return true if at the end of a record (or file)
inline bool skip_check_eor(istream &in) {
    skip(in);
    int c = in.peek();
    return (c == EOF || c == '.');
}

// Return true if at the end of file
inline bool skip_check_eof(istream &in) {
    skip(in);
    int c = in.peek();
    return (c == EOF);
}


}
#define fmt(x) (static_cast<const std::ostringstream&>(std::ostringstream() << x).str())

#define UNUSED(x) (void)(x)

#endif //LIBTRELLIS_UTIL_HPP
