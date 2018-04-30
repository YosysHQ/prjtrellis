#ifndef LIBTRELLIS_CRAM_HPP
#define LIBTRELLIS_CRAM_HPP

#include <cstdint>
#include <memory>
#include <vector>

using namespace std;

// This represents a view into the configuration memory, typically used to represent a tile
class CRAMView {
public:
    // Access a bit inside the CRAM view by frame and bit offset within the view
    inline bool &bit(int frame, int bit);
    // Return the number of frames inside the view
    int frames() const;
    // Return the number of bits inside the view
    int bits() const;

private:
    // Private constructor, CRAM::make_view should always be used
    CRAMView(shared_ptr<vector<vector<bool>>> bits, int frame_offset, int bit_offset, int frame_count, int bit_count);

    int frame_offset;
    int bit_offset;
    int frame_count;
    int bit_count;
    friend class CRAM;
};

// This represents the chip configuration RAM, and allows views of it to be made (for tile accesses)
// N.B. all accesses are in the format (frame, bit)
class CRAM {
public:
    // Construct empty CRAM given size
    CRAM(int frames, int bits);
    // Access a bit in the CRAM given frame and bit offset
    inline bool &bit(int frame, int bit);
    // Return number of frames in CRAM
    int frames() const;
    // Return number of bits per frame in CRAM
    int bits() const;
    // Make a view to the CRAM given frame and bit offset; and frames and bits per frame in the view
    CRAMView make_view(int frame_offset, int bit_offset, int frame_count, int bit_count);
private:
    // Using a shared_ptr so views are not invalidated even if the CRAM itself is deleted
    shared_ptr<vector<vector<bool>>> data;
};

#endif //LIBTRELLIS_CRAM_HPP
