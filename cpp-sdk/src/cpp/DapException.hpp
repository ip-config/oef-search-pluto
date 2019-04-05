#pragma once
#include <exception>
#include <string>

class DapException:public std::exception
{
public:
  DapException(int the_code, const std::string &the_msg) noexcept
    :code(the_code),
     msg(the_msg)
  {
  }
  ~DapException() = default;

  DapException(const DapException &other) noexcept
  {
    code = other.code;
    msg = other.msg;
  }

  DapException& operator=(const DapException &other) noexcept
  {
    code = other.code;
    msg = other.msg;
    return *this;
  }

  virtual const char* what() const noexcept
  {
    return msg.c_str();
  }
protected:
  int code;
  std::string msg;
};
