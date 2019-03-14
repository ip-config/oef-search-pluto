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
  core.add(this);
  read_start();
}

void ChatClient::send(const std::string &s)
{
  outq.push_back(s);
  core.context -> post(std::bind(&ChatClient::write_start, this));
}

void ChatClient::write_complete(ChatCore &thecore, const boost::system::error_code& ec, const size_t &bytes)
{
  if (ec == boost::asio::error::eof || ec == boost::asio::error::operation_aborted)
  {
    thecore.gone(this);
    return;
  }

  if (ec)
  {
    thecore.error(this, ec);
    return;
  }

  core.context -> post(std::bind(&ChatClient::write_start, this));
  write_start();
}

void ChatClient::read_complete(ChatCore &thecore, const boost::system::error_code& ec, const size_t &bytes)
{
  if (ec == boost::asio::error::eof || ec == boost::asio::error::operation_aborted)
  {
    thecore.gone(this);
    return;
  }

  if (ec)
  {
    thecore.error(this, ec);
    return;
  }

  if (bytes > 0)
  {
    std::string s;
    std::istream is(&read_buffer);
    std::getline(is, s, '\n');

    while(s.length() &&
          (
           s[s.length()-1]=='\n'
          ||
          s[s.length()-1]=='\r'
           )
          )
    {
      s.pop_back();
    }

    inq.push_back(s);
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
                                       std::ref(core),
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
                                          std::ref(core),
                                          std::placeholders::_1,
                                          std::placeholders::_2
                                          )
                                );
}

void ChatClient::in_work()
{
  if (inq.size())
  {
    auto a = inq.front();
    if (a == "exit" || a == "quit")
    {
      sock.close();
      return;
    }

    core.message(this, a + "\n");
    inq.pop_front();
    core.context -> post(std::bind(&ChatClient::in_work, this));
  }
}

