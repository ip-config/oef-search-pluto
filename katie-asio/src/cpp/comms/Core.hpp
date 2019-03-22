#pragma once
#include <memory>
#include <boost/asio.hpp>

using boost::asio::ip::tcp;

class Core
{
public:
  std::shared_ptr<boost::asio::io_context> context;

  Core();
  virtual ~Core();

  void run(void);

  operator boost::asio::io_context*() { return context.get(); }
  operator boost::asio::io_context&() { return *context; }
};
