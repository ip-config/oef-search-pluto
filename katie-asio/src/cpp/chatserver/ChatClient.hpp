#pragma once
#include "katie-asio/src/cpp/comms/Listener.hpp"

#include <list>

class ChatCore;

class ChatClient:public Listener::ISocketOwner
{
public:
  ChatClient(ChatCore &thecore);
  virtual ~ChatClient();

  ChatCore &core;
  tcp::socket sock;
  boost::asio::streambuf read_buffer;
  std::list<std::string> outq;
  std::list<std::string> inq;

  virtual tcp::socket& socket();
  virtual void go();
  virtual void send(const std::string &s);
  void write_complete(ChatCore &thecore, const boost::system::error_code&, const size_t &bytes);
  void read_complete(ChatCore &thecore, const boost::system::error_code&, const size_t &bytes);
  void write_start();
  void read_start();
  void in_work();
};

