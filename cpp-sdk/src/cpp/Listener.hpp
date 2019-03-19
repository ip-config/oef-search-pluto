#pragma once

#include "cpp-sdk/src/cpp/Transport.hpp"
#include "TransportFactory.hpp"

#include "boost/asio.hpp"

#include <memory>
#include <unordered_map>

using boost::asio::ip::tcp;


class Listener : public std::enable_shared_from_this<Listener>, public IDestroyer
{
public:
  Listener();
  virtual ~Listener();

  void start_accept();
  void run(){
    io_context.run();
  }

  virtual void destroy(uint16_t id){
    std::cerr << "Remove id=" << id <<" from transport store!" <<std::endl;
    transports_.erase(id);
  }

  std::shared_ptr<tcp::acceptor> acceptor;

  boost::asio::io_context io_context;

  std::unordered_map<uint16_t, std::shared_ptr<Transport>> transports_;
  uint16_t curr_id_ = 0;

  TransportFactory transportFactory_;

};
