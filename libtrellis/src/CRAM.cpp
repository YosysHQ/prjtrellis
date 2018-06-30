#include "CRAM.hpp"
#include <cassert>

namespace Trellis {
char &CRAMView::bit(int frame, int bit) const {
    assert(frame < frame_count);
    assert(bit < bit_count);
    return cram_data->at(frame_offset + frame).at(bit_offset + bit);
}

int CRAMView::frames() const { return frame_count; }

int CRAMView::bits() const { return bit_count; }

bool CRAMView::get_bit(int frame, int biti) const {
    return bool(bit(frame, biti));
}

void CRAMView::set_bit(int frame, int biti, bool value) {
    bit(frame, biti) = value;
}

CRAMView::CRAMView(shared_ptr<vector<vector<char>>> data, int frame_offset, int bit_offset, int frame_count,
                   int bit_count)
        : frame_offset(frame_offset), bit_offset(bit_offset), frame_count(frame_count),
          bit_count(bit_count), cram_data(data) {}

void CRAMView::clear() {
    for (int i = 0; i < frame_count; i++) {
        for (int j = 0; j < bit_count; j++) {
            bit(i, j) = 0;
        }
    }
}

CRAMDelta operator-(const CRAMView &a, const CRAMView &b) {
    if ((a.bits() != b.bits()) || (a.frames() != b.frames()))
        throw runtime_error("cannot compare CRAMViews of different sizes");
    CRAMDelta delta;
    for (int i = 0; i < a.frames(); i++) {
        for (int j = 0; j < b.bits(); j++) {
            if (a.bit(i, j) != b.bit(i, j)) {
                delta.push_back(ChangedBit{i, j, int(a.bit(i, j)) - int(b.bit(i, j))});
            }
        }
    }
    return delta;
}

CRAM::CRAM(int frames, int bits) {
    data = make_shared<vector<vector<char>>>();
    data->resize(frames, vector<char>(bits));
}

char &CRAM::bit(int frame, int bit) const {
    return data->at(frame).at(bit);
}

bool CRAM::get_bit(int frame, int biti) const {
    return bool(bit(frame, biti));
}

void CRAM::set_bit(int frame, int biti, bool value) {
    bit(frame, biti) = value;
}

int CRAM::frames() const { return int(data->size()); }

int CRAM::bits() const { return int(data->at(0).size()); }

CRAMView CRAM::make_view(int frame_offset, int bit_offset, int frame_count, int bit_count) {
    return CRAMView(data, frame_offset, bit_offset, frame_count, bit_count);
}

}
