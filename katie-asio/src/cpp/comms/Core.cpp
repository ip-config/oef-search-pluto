#include "Core.hpp"

Core::Core()
{
  context = std::make_shared<boost::asio::io_context>();
}

Core::~Core()
{
}


void Core::run()
{
  context -> run();
}
