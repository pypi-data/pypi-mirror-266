#pragma once

#include <string>
#include <vector>

#include <pcl/PCLPointCloud2.h>
#include <pcl/io/pcd_io.h>


namespace my_library {
class PCDReader {
 public:
  PCDReader();

  int read(std::string filename);

  int get_height();
  int get_width();

  std::vector<float> get_x();
  std::vector<float> get_y();
  std::vector<float> get_z();
  std::vector<float> get_intensity();
  std::vector<double> get_timestamp();
  std::vector<uint16_t> get_ring();

 private:
  pcl::PCDReader p;
  pcl::PCLPointCloud2 cloud;
  int height;
  int width;

  std::vector<float> x;
  std::vector<float> y;
  std::vector<float> z;
  std::vector<float> intensity;
  std::vector<double> timestamp;
  std::vector<uint16_t> ring;
};

}  // namespace my_library
