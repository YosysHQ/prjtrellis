#include "CRAM.hpp"
#include <cassert>

namespace Trellis {
char &CRAMView::bit(int frame, int bit) {
    assert(frame < frame_count);
    assert(bit < bit_count);
    return cram_data->at(frame_offset + frame).at(bit_offset + bit);
}

int CRAMView::frames() const { return frame_count; }

int CRAMView::bits() const { return bit_count; }

CRAMView::CRAMView(shared_ptr<vector<vector<char>>> data, int frame_offset, int bit_offset, int frame_count,
                   int bit_count)
        : cram_data(data), frame_offset(frame_offset), bit_offset(bit_offset), frame_count(frame_count),
          bit_count(bit_count) {};

CRAM::CRAM(int frames, int bits) {
    data = make_shared<vector<vector<char>>>();
    data->resize(frames, vector<char>(bits));
}

char &CRAM::bit(int frame, int bit) {
    return data->at(frame).at(bit);
}

int CRAM::frames() const { return int(data->size()); }

int CRAM::bits() const { return int(data->at(0).size()); }

CRAMView CRAM::make_view(int frame_offset, int bit_offset, int frame_count, int bit_count) {
    return CRAMView(data, frame_offset, bit_offset, frame_count, bit_count);
}
}