#pragma once
#include "katie-asio/src/cpp/comms/Core.hpp"

#include <list>

class ChatClient;

class ChatCore:public Core
{
public:
  ChatCore();
  virtual ~ChatCore();

  std::list<ChatClient*> clients;

  void add(ChatClient *client);
  void gone(ChatClient *client);
  void error(ChatClient *client, const boost::system::error_code &ec);
  void message(ChatClient *client, const std::string &m);
};
