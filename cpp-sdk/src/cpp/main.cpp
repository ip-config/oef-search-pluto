#include <list>
#include <iostream>
#include <functional>

#include "Listener.hpp"


int main(int argc, char *argv[])
{
  std::cout << "Hello"<< std::endl;


  std::shared_ptr<Listener> listener = std::make_shared<Listener>();
  listener->start_accept();
  listener->run();
}
