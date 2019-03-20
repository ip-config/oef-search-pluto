#include <iostream>

#include "katie-pb/src/protos/testmessage.pb.h"

#include <iostream>
#include <list>
#include <boost/asio.hpp>

class char_array_buffer : public std::streambuf
{
public:
  std::list<boost::asio::mutable_buffer> &buffers;
  int current;
  int size;

  char_array_buffer(std::list<boost::asio::mutable_buffer> &thebuffers):buffers(thebuffers)
  {
    current=0;
    size = 0;
    for(auto &b :  buffers)
    {
      size += boost::asio::buffer_size(b);
    }
  }

  char get_char_at(int pos)
  {
    int buf = 0;
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
        return r;
      }
    }
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

int main(int argc, char *argv[])
{
  std::cout << "Hello" << std::endl;

  TestMessage tm;

  tm.set_verb("get");
  tm.add_noun("book");
  tm.add_noun("bottle");
  tm.add_noun("box");

  size_t size = tm.ByteSizeLong();
  std::cout << size << std::endl;
  char *buffer = (char*)malloc(size);
  tm.SerializeToArray(buffer, size);

  TestMessage tm3;
  std::string s(buffer, size);
  std::cout << tm3.ParseFromString(s) << std::endl;

  std::cout << tm3.verb() << std::endl;
  for (int j = 0; j < tm3.noun_size(); j++) {
    std::cout << tm3.noun(j) << std::endl;
  }

  char *buffer1 = new char[10];
  char *buffer2 = new char[size - 10];

  memcpy(buffer1, buffer, 10);
  memcpy(buffer2, buffer+10, size-10);

  boost::asio::mutable_buffer mb1(buffer1, 10);
  boost::asio::mutable_buffer mb2(buffer2, size-10);

  std::list<boost::asio::mutable_buffer> buffers;

  buffers.push_back(mb1);
  buffers.push_back(mb2);

  char_array_buffer cb(buffers);

  TestMessage tm2;
  std::istream is(&cb);
  std::cout << tm2.ParseFromIstream(&is) << std::endl;

  std::cout << tm2.verb() << std::endl;
  for (int j = 0; j < tm2.noun_size(); j++) {
    std::cout << tm2.noun(j) << std::endl;
  }
}
