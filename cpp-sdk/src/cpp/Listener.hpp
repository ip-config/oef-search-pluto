#pragma once
#include <memory>
#include "boost/asio.hpp"
#include "cpp-sdk/src/cpp/ProtoFactory.hpp"


using boost::asio::ip::tcp;


class Listener
{
public:

  class ISocketOwner
  {
  public:
    ISocketOwner() {}
    virtual ~ISocketOwner() {}
    virtual tcp::socket& socket() = 0;
    virtual void go() = 0;
  };

  Listener();
  virtual ~Listener();

  void start_accept();
  void run(){
    io_context.run();
  }

  std::shared_ptr<tcp::acceptor> acceptor;

  boost::asio::io_context io_context;

  ProtoFactory protoFactory_;
};
