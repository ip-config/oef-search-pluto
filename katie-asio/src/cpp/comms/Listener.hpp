#pragma once
#include <memory>
#include <boost/asio.hpp>

using boost::asio::ip::tcp;

class Core;

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

  Listener(Core &core);
  virtual ~Listener();

  void start_accept();
  void handle_accept(ISocketOwner *new_connection, const boost::system::error_code& error);

  std::shared_ptr<tcp::acceptor> acceptor;

  using CONN_CREATOR = std::function< ISocketOwner* ()>;

  CONN_CREATOR creator;
  Core &core;
};
