#include "Tile.hpp"
#include "Chip.hpp"

namespace Trellis {
Tile::Tile(Trellis::TileInfo info, Trellis::Chip &parent) : info(info), cram(parent.cram.make_view(info.frame_offset,
                                                                                                   info.bit_offset,
                                                                                                   info.num_frames,
                                                                                                   info.bits_per_frame)) {}

}
