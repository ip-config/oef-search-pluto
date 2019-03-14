#include <list>
#include <iostream>
#include <functional>

#include "ChatClient.hpp"
#include "ChatCore.hpp"

Listener::ISocketOwner *createNewConnection(ChatCore &core)
{
  auto obj = new ChatClient(core);
  return obj;
}


int main(int argc, char *argv[])
{
  std::cout << "Hello"<< std::endl;

  ChatCore core;

  Listener listener(core);
  listener.creator = std::bind(createNewConnection, std::ref(core));

  listener.start_accept();

  core.run();
}
