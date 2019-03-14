#include "katie-asio/src/cpp/chatserver/ChatCore.hpp"

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

