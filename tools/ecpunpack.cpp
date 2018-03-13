#include <stdint.h>
#include <vector>
#include <map>
#include <string>
#include <iostream>
#include <iomanip>
#include <fstream>
#include <assert.h>
#include <string.h>

#define CRC16_POLY 0x8005

// From TN1260
enum BitstreamCommands {
  LSC_RESET_CRC           = 0b00111011,
  VERIFY_ID               = 0b11100010,
  LSC_WRITE_COMP_DIC      = 0b00000010,
  LSC_PROG_CNTRL0         = 0b00100010,
  LSC_INIT_ADDRESS        = 0b01000110,
  LSC_PROG_INCR_CMP       = 0b10111000,
  LSC_PROG_INCR_RTI       = 0b10000010,
  LSC_PROG_SED_CRC        = 0b10100010,
  ISC_PROGRAM_SECURITY    = 0b11001110,
  ISC_PROGRAM_USERCODE    = 0b11000010,
  LSC_EBR_ADDRESS         = 0b11110110,
  LSC_EBR_WRITE           = 0b10110010,
  ISC_PROGRAM_DONE        = 0b01011110,
  DUMMY                   = 0b11111111,

};

struct DeviceInfo {
  std::string name;
  uint32_t idcode;
  int n_frames;
  int frame_data_bits;
  int frame_pad_bits;
};

DeviceInfo devices[] = {
  {"LFE5U-25",  0x41111043, 7562,   592, 0},
  {"LFE5U-45",  0x41112043, 9470,   846, 2},
  {"LFE5U-85",  0x41113043, 13294, 1136, 0},
  {"LFE5UM-25", 0x01111043, 7562,   592, 0},
  {"LFE5UM-45", 0x01112043, 9470,   846, 2},
  {"LFE5UM-85", 0x01113043, 13294, 1136, 0},
};

const uint8_t preamble[0x8] = {0xFF, 0xFF, 0xBD, 0xB3, 0xFF, 0xFF, 0xFF, 0xFF};

class Bitstream {
public:
  Bitstream(uint8_t *_dat, int _len) : dat(_dat), len(_len) {};
  Bitstream(std::string file) {
    std::ifstream ifs(file, std::ios::binary|std::ios::ate);
    std::ifstream::pos_type pos = ifs.tellg();
    len = pos;
    dat = new uint8_t[len];
    ifs.seekg(0, std::ios::beg);
    ifs.read((char *)dat, len);
  }

  uint8_t GetByte() {
    assert(idx < len);
    uint8_t val = dat[idx++];
    UpdateCRC16(val);
    return val;
  }

  void GetBytes(uint8_t *out, int count) {
    for(int i = 0; i < count; i++) out[i] = GetByte();
  }

  void SkipBytes(int count) {
    for(int i = 0; i < count; i++) GetByte();
  }

  uint32_t GetUint32() {
    uint8_t tmp[4];
    GetBytes(tmp, 4);
    return (tmp[0] << 24UL) | (tmp[1] << 16UL) | (tmp[2] << 8UL) | (tmp[3]);
  }

  void UpdateCRC16(uint8_t val) {
    int bit_flag;
    for(int i = 7; i >= 0; i--) {
      bit_flag = crc16 >> 15;

      /* Get next bit: */
      crc16 <<= 1;
      crc16 |= (val >> i) & 1; // item a) work from the least significant bits

      /* Cycle check: */
      if(bit_flag)
          crc16 ^= CRC16_POLY;
    }

  }

  bool FindPreamble(const uint8_t *preamble, int pre_len) {
    for(int i = idx; i <= (len - pre_len); i++) {
      if(memcmp(preamble, dat+i, pre_len) == 0) {
        std::cerr << "found preamble at offset " << std::dec << i << std::endl;
        idx = i + pre_len;
        return true;
      }
    }
    return false;
  }

  uint16_t GetCRC16() {
    // item b) "push out" the last 16 bits
    int i, bit_flag;
    for (i = 0; i < 16; ++i) {
        bit_flag = crc16 >> 15;
        crc16 <<= 1;
        if(bit_flag)
            crc16 ^= CRC16_POLY;
    }

    return crc16;
  }
  void ResetCRC16() { crc16 = 0; }
  bool CheckCRC16() {
      /*TODO*/
    uint16_t act_crc = GetCRC16();
    uint8_t crc_bytes[2];
    GetBytes(crc_bytes, 2);
    uint16_t exp_crc = (crc_bytes[0] << 8) | crc_bytes[1];
    if(act_crc != exp_crc)
      std::cerr << "crc fail, calculated " << std::hex << act_crc << ", expected " << exp_crc << std::endl;
    ResetCRC16();
    return exp_crc == act_crc;
  }

  bool Done() {
    return (idx >= len);
  }
private:
  uint16_t crc16 = 0x0;
  uint8_t *dat;
  int len;
  int idx = 0;
};

struct ChipConfig {

  ChipConfig(DeviceInfo _dev) : dev(_dev) {
    chip.resize(dev.n_frames);
    for(int i = 0; i < dev.n_frames; i++)
      chip[i].resize(dev.frame_data_bits, false);
  };

  void LoadFrame(int frame, Bitstream &bs) {
    int frame_bytes = (dev.frame_data_bits + dev.frame_pad_bits) / 8;
    uint8_t *data = new uint8_t[frame_bytes];
    bs.GetBytes(data, frame_bytes);
    for(int i = 0; i < dev.frame_data_bits; i++) {
      int ofs = i + dev.frame_pad_bits;
      chip[(dev.n_frames-1) - frame][i] = (data[(frame_bytes - 1) - (ofs/8)] >> (ofs % 8)) & 0x01;
    }
    delete[] data;
  }

  DeviceInfo dev;
  std::vector<std::vector<bool>> chip;
};

/*
Random notes
CRC16 of frames uses the CRC16-BUYPASS algorithm (ignore references to bitswapping
in Lattice's docs, at least if using this) but includes the dummy 0xFF before frames.
*/

bool ParseCommand(Bitstream &bs, ChipConfig &c) {
  uint8_t cmd = bs.GetByte();
  switch(cmd) {
    case LSC_RESET_CRC:
      std::cerr << "reset CRC" << std::endl;
      bs.SkipBytes(3);
      bs.ResetCRC16();
      break;
    case VERIFY_ID: {
      bs.SkipBytes(3);
      uint32_t id = bs.GetUint32();
      std::cerr << "verify device ID 0x"  << std::hex << id << std::endl;
      bool found = false;
      for(auto dev : devices) {
        if(dev.idcode == id) {
          std::cerr << "identified device " << dev.name << std::endl;
          found = true;
          c = ChipConfig(dev);
          break;
        }
      }
      if(!found) {
        std::cerr << "unknown device ID" << std::endl;
        return false;
      }
    } break;
    case LSC_PROG_CNTRL0: {
      bs.SkipBytes(3);
      uint32_t cfg = bs.GetUint32();
      std::cerr << "set control reg 0 to 0x" << std::hex << cfg << std::endl;
    } break;
    case LSC_INIT_ADDRESS:
      bs.SkipBytes(3);
      std::cerr << "reset frame address" << std::endl;
      break;
    case LSC_PROG_INCR_RTI: {
      uint8_t params[3];
      bs.GetBytes(params, 3);
      int dummy_bytes = (params[0] & 0x0F);
      int frame_count = (params[1] << 8) | params[2];
      std::cerr << "reading " << std::dec << frame_count << " config frames (with " << std::dec << dummy_bytes << " dummy bytes)" << std::endl;
      uint8_t crc[2];
      for(int i = 0; i < frame_count; i++) {
        c.LoadFrame(i, bs);
        // TODO: CRC
        bs.CheckCRC16();
        bs.SkipBytes(dummy_bytes);
      }
      bs.ResetCRC16();
      break;
    }
    case LSC_PROG_SED_CRC:
      std::cerr << "load SED CRC" << std::endl;
      bs.SkipBytes(7);
      break;
    case ISC_PROGRAM_SECURITY:
      std::cerr << "program security" << std::endl;
      bs.SkipBytes(3);
      break;
    case ISC_PROGRAM_USERCODE: {
      bs.SkipBytes(3);
      uint32_t uc = bs.GetUint32();
      bs.SkipBytes(2);

      std::cerr << "set usercode to 0x" << std::hex << uc << std::endl;
    } break;
    // TODO: EBR writes
    case ISC_PROGRAM_DONE:
      std::cerr << "program DONE" << std::endl;
      bs.SkipBytes(3);
      break;
    case DUMMY:
      break;
    default:
      std::cerr << "unknown command "  << std::hex << int(cmd) << std::endl;
      return false;
  }
  return true;
}

int main(int argc, char *argv[]) {
  if(argc < 2) {
    std::cerr << "usage: ecpunpack bitstream.bit" << std::endl;
    return 2;
  }
  Bitstream bs = Bitstream(std::string(argv[1]));
  ChipConfig cc(devices[2]);
  if(!bs.FindPreamble(preamble, 8)) {
    return 1;
  }
  while(ParseCommand(bs, cc) && !bs.Done())
    ;
  if(!bs.Done())
    return 1;
  std::cerr << "dumping configuration" << std::endl;
  for(int f = 0; f < cc.dev.n_frames; f++) {
    for(int b = 0; b < cc.dev.frame_data_bits; b++) {
      if(cc.chip[f][b])
        std::cout << std::dec << "(" << b << ", " << f << ")" << std::endl;
    }
  }
  return 0;
}
