#include "pcd_reader.h"

namespace my_library {
PCDReader::PCDReader() {}

int PCDReader::read(std::string filename) {
  int ret = p.read(filename, cloud);
  if (ret == -1) {
    return ret;
  }
  x.resize(cloud.width);
  y.resize(cloud.width);
  z.resize(cloud.width);
  intensity.resize(cloud.width);
  timestamp.resize(cloud.width);
  ring.resize(cloud.width);
  for (int i; i < cloud.width; ++i) {
    x[i] = reinterpret_cast<const float&>(cloud.data[i * cloud.point_step + 0]);
    y[i] = reinterpret_cast<const float&>(cloud.data[i * cloud.point_step + 4]);
    z[i] = reinterpret_cast<const float&>(cloud.data[i * cloud.point_step + 8]);
    intensity[i] = reinterpret_cast<const float&>(cloud.data[i * cloud.point_step + 12]);
    timestamp[i] = reinterpret_cast<const double&>(cloud.data[i * cloud.point_step + 16]);
    ring[i] = reinterpret_cast<const uint16_t&>(cloud.data[i * cloud.point_step + 24]);
  }
  return 0;
}

int PCDReader::get_height() { return cloud.height; }

int PCDReader::get_width() { return cloud.width; }

std::vector<float> PCDReader::get_x() { return x; }

std::vector<float> PCDReader::get_y() { return y; }

std::vector<float> PCDReader::get_z() { return z; }

std::vector<float> PCDReader::get_intensity() { return intensity; }

std::vector<double> PCDReader::get_timestamp() { return timestamp; }

std::vector<uint16_t> PCDReader::get_ring() { return ring; }

}  // namespace my_library
