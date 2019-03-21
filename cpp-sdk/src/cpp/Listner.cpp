#include "Listener.hpp"

#include <functional>


Listener::Listener(uint16_t port, std::shared_ptr<TransportFactory> transport_factory)
 : transport_factory_(std::move(transport_factory))
{
  acceptor_ = std::make_shared<tcp::acceptor>(io_context_, tcp::endpoint(tcp::v4(), port));
}

void Listener::start_accept()
{
  acceptor_ -> async_accept([this](std::error_code ec, tcp::socket socket){
    std::shared_ptr<Transport> transport = std::make_shared<Transport>(std::move(socket), curr_id_);

    transport->SetDestroyer(shared_from_this());
    transport_factory_->SetReadCallbacks(transport);

    transport->go();

    transports_[curr_id_++] = std::move(transport);

    start_accept();
  });
}


Listener::~Listener()
{
  for(auto& tp : transports_){
    tp.second->close();
  }
  transports_.clear();
}
