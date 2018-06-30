#ifndef LIBTRELLIS_CRAM_HPP
#define LIBTRELLIS_CRAM_HPP

#include <cstdint>
#include <memory>
#include <vector>

using namespace std;
namespace Trellis {
// This represents the difference between two CRAMViews
struct ChangedBit {
    int frame;
    int bit;
    int delta; // -1, 0 or +1 (false-true, equal, true-false)
    inline bool operator==(const ChangedBit &other) {
        return (frame == other.frame) && (bit == other.bit) && (delta == other.delta);
    }
};

typedef vector<ChangedBit> CRAMDelta;

// This represents a view into the configuration memory, typically used to represent a tile
class CRAMView {
public:
    // Access a bit inside the CRAM view by frame and bit offset within the view
    char &bit(int frame, int bit) const;

    // Primarily for Python use
    bool get_bit(int frame, int biti) const;

    void set_bit(int frame, int biti, bool value);

    // Return the number of frames inside the view
    int frames() const;

    // Return the number of bits inside the view
    int bits() const;

    // Clear the CRAM region
    void clear();

    friend CRAMDelta operator-(const CRAMView &a, const CRAMView &b);

private:
    // Private constructor, CRAM::make_view should always be used
    CRAMView(shared_ptr<vector<vector<char>>> data, int frame_offset, int bit_offset, int frame_count, int bit_count);

    int frame_offset;
    int bit_offset;
    int frame_count;
    int bit_count;

    friend class CRAM;

    shared_ptr<vector<vector<char>>> cram_data;
};

CRAMDelta operator-(const CRAMView &a, const CRAMView &b);

// This represents the chip configuration RAM, and allows views of it to be made (for tile accesses)
// N.B. all accesses are in the format (frame, bit)
class CRAM {
public:
    // Construct empty CRAM given size
    CRAM(int frames, int bits);

    // Access a bit in the CRAM given frame and bit offset
    char &bit(int frame, int bit) const;

    // Primarily for Python use
    bool get_bit(int frame, int biti) const;

    void set_bit(int frame, int biti, bool value);

    // Return number of frames in CRAM
    int frames() const;

    // Return number of bits per frame in CRAM
    int bits() const;

    // Make a view to the CRAM given frame and bit offset; and frames and bits per frame in the view
    CRAMView make_view(int frame_offset, int bit_offset, int frame_count, int bit_count);

private:
    // Using a shared_ptr so views are not invalidated even if the CRAM itself is deleted
    // A vector of type char is used as the optimisations in vector<bool> are not worth the loss of bool& etc
    shared_ptr<vector<vector<char>>> data;
};
}
#endif //LIBTRELLIS_CRAM_HPP
