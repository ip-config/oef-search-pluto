#include <functional>

#include "Listener.hpp"
#include "boost/asio/ip/tcp.hpp"
#include "cpp-sdk/src/cpp/Transport.hpp"

Listener::Listener()
{
  acceptor = std::make_shared<tcp::acceptor>(io_context, tcp::endpoint(tcp::v4(), 7600));
}

void Listener::start_accept()
{
  acceptor -> async_accept([this](std::error_code ec, tcp::socket socket){
    Transport transport(std::move(socket));
    transport.go();
    start_accept();
  });
}


Listener::~Listener()
{
}
