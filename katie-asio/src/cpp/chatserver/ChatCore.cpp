#include "katie-asio/src/cpp/chatserver/ChatCore.hpp"

#include <iostream>

#include "ChatClient.hpp"

ChatCore::ChatCore()
{
}
ChatCore::~ChatCore()
{
}


void ChatCore::add(ChatClient *client)
{
  clients.push_back(client);
}

void ChatCore::gone(ChatClient *client)
{
  clients.remove_if([client](ChatClient *cand){ return cand == client; });
}

void ChatCore::error(ChatClient *client, const boost::system::error_code &ec)
{
  std::cout << "ERROR:" << client << ":" << ec.message() << std::endl;
  gone(client);
}

void ChatCore::message(ChatClient *client, const std::string &m)
{
  for(auto c : clients)
  {
    if (c != client)
    {
      c -> send(m);
    }
  }
}
