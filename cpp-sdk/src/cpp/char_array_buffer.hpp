#pragma once

#include <iostream>
#include <list>
#include <vector>
#include <ctype.h>
#include "boost/asio.hpp"

class char_array_buffer : public std::streambuf
{
public:
  std::vector<boost::asio::mutable_buffer> &buffers;
  int current;
  int size;

  char_array_buffer(std::vector<boost::asio::mutable_buffer> &thebuffers):buffers(thebuffers)
  {
    current=0;
    size = 0;
    for(auto &b :  buffers)
    {
      size += boost::asio::buffer_size(b);
    }
  }

  void diagnostic()
  {
    for(int i=0;i<size;i++)
    {
      char c = get_char_at(i,true);

      switch(c)
      {
        case 10:
          std::cout << "\\n";
          break;
        default:
          if (::isprint(c))
          {
            std::cout << c;
          }
          else
          {
            int cc = (unsigned char)c;
            std::cout << "\\x";
            for(int j=0;j<2;j++)
            {
              std::cout << "0123456789ABCDEF"[((cc&0xF0) >> 4)];
              cc <<= 4;
            }
          }
      }
    }
    std::cout << std::endl;
  }

  char get_char_at(int pos, bool silent = false)
  {
    int buf = 0;

    if (pos >= size)
    {
      if (!silent)
        std::cout << "pos=" << pos << " c=eof" << std::endl;
      return traits_type::eof();
    }

    for(auto &b :  buffers)
    {
      int c = boost::asio::buffer_size(b);
      if (pos >= c)
      {
        pos -= c;
        buf++;
      }
      else
      {
        auto r = boost::asio::buffer_cast<unsigned char*>(b)[pos];
        if (!silent)
          std::cout << "pos=" << pos << " c=" << int(r) << std::endl;
        return r;
      }
    }
    if (!silent)
      std::cout << "pos=" << pos << " c=eof" << std::endl;
    return traits_type::eof();
  }

  char_array_buffer::int_type underflow()
  {
    if (current >= size)
      return traits_type::eof();
    return traits_type::to_int_type(get_char_at(current));
  }
  char_array_buffer::int_type uflow()
  {
    if (current >= size)
      return traits_type::eof();
    auto r = traits_type::to_int_type(get_char_at(current));
    current += 1;
    return r;
  }

  std::streamsize showmanyc()
  {
    return (std::streamsize)size;
  }
  int_type pbackfail(int_type ch)
  {
    return traits_type::eof();
  }
private:

  // copy ctor and assignment not implemented;
  // copying not allowed
  char_array_buffer(const char_array_buffer &);
  char_array_buffer &operator= (const char_array_buffer &);
};