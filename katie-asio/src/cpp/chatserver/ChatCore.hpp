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
  void message(ChatClient *client, const std::string &m);
};

