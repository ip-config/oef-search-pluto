#include "katie-asio/src/cpp/chatserver/ChatClient.hpp"

#include <iostream>

#include "ChatCore.hpp"

ChatClient::ChatClient(ChatCore &thecore):core(thecore), sock(core)
{
}

ChatClient::~ChatClient()
{
}


tcp::socket& ChatClient::socket()
{
  return sock;
}
void ChatClient::go()
{
  std::cout << "natter" << std::endl;
  core.add(this);
  read_start();
}

void ChatClient::send(const std::string &s)
{
  outq.push_back(s);
  core.context -> post(std::bind(&ChatClient::write_start, this));
}

void ChatClient::write_complete(const boost::system::error_code&, const size_t &bytes)
{
  core.context -> post(std::bind(&ChatClient::write_start, this));
  write_start();
}

void ChatClient::wibble(const boost::system::error_code&ec, const size_t &bytes)
{
}

void ChatClient::read_complete(const boost::system::error_code&ec, const size_t &bytes)
{
  std::cout << " ec=" << ec << " bytes=" <<bytes<<std::endl;
  if (bytes > 0)
  {
    std::string s;
    std::istream is(&read_buffer);
    is >> s;
    if (s!="\n")
    {
      inq.push_back(s);
      std::cout << "R:" << s << std::endl;
    }
    core.context -> post(std::bind(&ChatClient::in_work, this));
  }
  read_start();
}

void ChatClient::write_start()
{
  if (outq.size())
  {
    boost::asio::async_write(sock,
                             boost::asio::buffer(outq.front()),
                             std::bind(
                                       &ChatClient::write_complete,
                                       this,
                                       std::placeholders::_1,
                                       std::placeholders::_2
                                       )
                             );
    outq.pop_front();
  }
}

void ChatClient::read_start()
{
  boost::asio::async_read_until(sock,
                                read_buffer,
                                "\r\n",
                                std::bind(
                                          &ChatClient::read_complete,
                                          this,
                                          std::placeholders::_1,
                                          std::placeholders::_2
                                          )
                                );
}

void ChatClient::in_work()
{
  if (inq.size())
  {
    std::cout << "I:" << inq.front() << std::endl;
    core.message(this, inq.front());
    inq.pop_front();
    core.context -> post(std::bind(&ChatClient::in_work, this));
  }
}

