#include <functional>

#include "Listener.hpp"
#include "Core.hpp"

Listener::Listener(Core &thecore):core(thecore)
{
  acceptor = std::make_shared<tcp::acceptor>(*(core.context), tcp::endpoint(tcp::v4(), 7600));
}

void Listener::start_accept()
{
  ISocketOwner *new_connection = creator();
  acceptor -> async_accept(new_connection->socket(),
                           std::bind(&Listener::handle_accept, this, new_connection, std::placeholders::_1));
}

void Listener::handle_accept(ISocketOwner *new_connection, const boost::system::error_code& error)
{
  if (!error)
  {
    new_connection->go();
  }

  start_accept();
}

Listener::~Listener()
{
}
