#include <functional>

#include "Listener.hpp"
#include "boost/asio/ip/tcp.hpp"
#include "cpp-sdk/src/cpp/Transport.hpp"

std::vector<std::shared_ptr<Transport>> transports_;

Listener::Listener()
{
  acceptor = std::make_shared<tcp::acceptor>(io_context, tcp::endpoint(tcp::v4(), 7600));
}

void Listener::start_accept()
{
  acceptor -> async_accept([this](std::error_code ec, tcp::socket socket){
    std::shared_ptr<Transport> transport = std::make_shared<Transport>(std::move(socket), protoFactory_);
    transport->SetErrorCallback([](std::error_code ec){
      std::cerr << ec.message() << std::endl;
    });
    transport->go();
    transport->AddReadCallback<Query>("search", [](Query proto, Transport::TransportPtr tptr){
      std::cout << "QUERY: ";
      std::cout << proto.ttl() << " , " << proto.source_key() << std::endl;
    });
    transports_.push_back(std::move(transport));
    start_accept();
  });
}


Listener::~Listener()
{
}
