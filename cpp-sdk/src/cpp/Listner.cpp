#include "Listener.hpp"

#include "boost/asio/ip/tcp.hpp"

#include <functional>


Listener::Listener()
{
  acceptor = std::make_shared<tcp::acceptor>(io_context, tcp::endpoint(tcp::v4(), 7600));
}

void Listener::start_accept()
{
  acceptor -> async_accept([this](std::error_code ec, tcp::socket socket){
    std::shared_ptr<Transport> transport = std::make_shared<Transport>(std::move(socket), curr_id_);

    transport->SetDestroyer(shared_from_this());
    transportFactory_.SetReadCallbacks(transport);

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
