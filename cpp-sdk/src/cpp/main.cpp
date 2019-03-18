#include <list>
#include <iostream>
#include <functional>

#include "Listener.hpp"


int main(int argc, char *argv[])
{
  std::cout << "Hello"<< std::endl;


  Listener listener;
  listener.start_accept();
  listener.run();
}
