#pragma once

#include "asio_inc.hpp"

#include <cstddef>
#include <cstdint>
#include <vector>
#include <cstring>
#include <iostream>
#include <list>
#include <algorithm>


class CircularBuffer {
public:
  using Byte = uint8_t;
  CircularBuffer(uint32_t size)
  : buff_size_{size}
  , buff_{new Byte[buff_size_]}
  , r_{size-1}
  , w_{0}
  {
  }
  virtual ~CircularBuffer() {
    delete [] buff_;
  }

  std::vector<boost::asio::mutable_buffer> getBuffersToWrite(uint32_t size){
    uint32_t available = ((r_+buff_size_)-w_)%buff_size_;
    std::cout << "GETBUFFERSTOWRITE: " << buff_size_ << ", " << available  << ", r_=" << r_<<", w_=" << w_<< std::endl;
    if (available<size){
      resize(buff_size_*2);
      return getBuffersToWrite(size);
    }
    std::vector<boost::asio::mutable_buffer>  buffers;

    uint32_t w1 = w_%buff_size_;
    uint32_t size1 = std::min(w_+available, buff_size_)-w_;
    uint32_t s = std::min(size1, size);
    buffers.push_back(boost::asio::buffer(buff_+w1, s));
    w_ = (w1+s)%buff_size_;
    if (size1<size){
      uint32_t size2 = std::max(static_cast<uint32_t>(0), available-size1);
      std::cout << "CIRCBUF: r2=0, size="<<size2 << std::endl;
      buffers.push_back(boost::asio::buffer(buff_, size2));
      w_ = size2-1;
    }
    std::cout << "CIRCBUF: w1=" << w1 << ", size="<<s <<  "(size1=" << size1<< ") w_=" << w_<< std::endl;

    return buffers;
  }

  std::vector<boost::asio::mutable_buffer> getBuffersToRead(){
    uint32_t data_len = buff_size_- ((r_+buff_size_)-w_+1)%buff_size_;
    std::cout << "GETBUFFERSTOREAD: " << buff_size_ << ", " << data_len  << ", r_=" << r_<<", w_=" << w_<< std::endl;

    uint32_t r1 = (r_+1)%buff_size_;
   uint32_t size1 = std::min(r1+data_len, buff_size_)-r1;

   std::vector<boost::asio::mutable_buffer> buffers;
   buffers.push_back(boost::asio::buffer(buff_+r1, size1));
   r_ = (r_+size1) % buff_size_;
   if (size1<data_len){
     uint32_t size2 = std::max(static_cast<uint32_t>(0), data_len-size1);
     buffers.push_back(boost::asio::buffer(buff_, size2));
     r_ = size2-1;
   }
    std::cout << "CIRCBUF: r1=" << r1 <<" , size1=" << size1 << " r_=" << r_ <<", w_" <<w_ << std::endl;

    return buffers;
  }

private:
  void resize(uint32_t new_size) {
    Byte *new_buff = new Byte[new_size];
    uint32_t s = (r_+1) % buff_size_;
    if (s<=w_){
      std::memcpy(new_buff, buff_+s, w_-s);
      w_ = w_-s+1;
    } else {
      std::memcpy(new_buff, buff_+s, buff_size_-s);
      std::memcpy(new_buff+buff_size_-s, buff_, w_+1);
      w_ = buff_size_-s+w_+1;
    }
    delete [] buff_;
    buff_ = new_buff;
    buff_size_ = new_size;
    r_ = new_size;
  }

private:
  uint32_t buff_size_;
  Byte* buff_;
  uint32_t r_, w_;
};