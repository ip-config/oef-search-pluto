#pragma once

#include "asio.hpp"

#include "Transport.hpp"
#include "TransportFactory.hpp"

#include <memory>
#include <unordered_map>

using boost::asio::ip::tcp;


class Listener : public std::enable_shared_from_this<Listener>, public IDestroyer
{
public:
  Listener(uint16_t, std::shared_ptr<TransportFactory>);
  virtual ~Listener();

  void start_accept();
  void run(){
    io_context_.run();
  }

  virtual void destroy(uint16_t id){
    std::cerr << "Remove id=" << id <<" from transport store!" <<std::endl;
    transports_.erase(id);
  }

private:
  std::shared_ptr<tcp::acceptor> acceptor_;
  boost::asio::io_context io_context_;

  std::shared_ptr<TransportFactory> transport_factory_;

  std::unordered_map<uint16_t, std::shared_ptr<Transport>> transports_;
  uint16_t curr_id_ = 0;
};
