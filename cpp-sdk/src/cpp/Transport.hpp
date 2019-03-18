#pragma once

#include <iostream>
#include "boost/asio.hpp"
#include "boost/asio/ip/tcp.hpp"
#include "boost/asio/write.hpp"
#include "boost/asio/buffer.hpp"
#include "boost/coroutine2/all.hpp"
#include "boost/asio/strand.hpp"
#include "boost/asio/spawn.hpp"
#include "cpp-sdk/src/cpp/Listener.hpp"


class Transport : Listener::ISocketOwner{
public:
  using Socket    = boost::asio::ip::tcp::socket;
  using SocketPtr = std::shared_ptr<Socket>;
  using Buffer    = std::vector<uint8_t>;
  using BufferPtr = std::shared_ptr<Buffer>;
  using ReadCb    = std::function<void(const std::string& path, BufferPtr)>;
  using ErrorCb   = std::function<void(std::error_code)>;

  Transport(Socket socket)
  : socket_(std::move(socket))
  , strand_(socket_.get_io_context())
  {}
  virtual ~Transport() = default;

  virtual Socket& socket(){
    return socket_;
  }
  virtual void go(){
    read([](const std::string& path, BufferPtr){
      std::cout << "path" << std::endl;
    }, [](std::error_code ec){
      std::cerr << "error: " << ec.message() << std::endl;
    });
  }

  void write(BufferPtr data, const std::string& path="") {
    std::vector<boost::asio::const_buffer> buffers;
    auto path_size = static_cast<uint32_t>(path.size()+1);
    int32_t len = -static_cast<int32_t>(path_size);
    if (path.size()>1){
      buffers.emplace_back(boost::asio::buffer(&len, sizeof(len)));
      buffers.emplace_back(boost::asio::buffer(&path, path_size));
    }

    auto data_len = static_cast<uint32_t>(data->size());
    buffers.emplace_back(boost::asio::buffer(&data_len, sizeof(data_len)));
    buffers.emplace_back(boost::asio::buffer(data->data(), data_len));


    uint32_t total = -len+sizeof(len)+data_len+sizeof(data_len);
    boost::asio::async_write(socket_, buffers, [data, total](std::error_code ec,  std::size_t length){
      if (ec){
        std::cerr << "Failed to write to socket, because: " << ec.message() << "! "
                  << length <<" bytes written out of " << total << std::endl;
      }
    });
  }


  void read(ReadCb cb, ErrorCb errorCb) {
    boost::asio::spawn(strand_, [this, cb, errorCb](boost::asio::yield_context yield){
      auto len = std::make_shared<int32_t>();
      boost::system::error_code ec;
      boost::asio::async_read(
          socket_,
          boost::asio::buffer(len.get(), sizeof(int32_t)),
          yield
      );
      if (ec){
        errorCb(ec);
        return ;
      }
      std::string path = "";
      if (len<0){
        auto path_ptr = std::make_shared<std::string>();
        boost::asio::async_read(
            socket_,
            boost::asio::buffer(path_ptr.get(), -(*len)),
            yield
        );
        if (ec){
          errorCb(ec);
          return;
        }
        path = *path_ptr;
        boost::asio::async_read(
            socket_,
            boost::asio::buffer(len.get(), sizeof(int32_t)),
            yield
        );
        if (ec){
          errorCb(ec);
          return;
        }
      }
      BufferPtr buffer = std::make_shared<Buffer>(len);
      boost::asio::async_read(
          socket_,
          boost::asio::buffer(buffer->data(), *len),
          yield
      );
      if (ec){
        errorCb(ec);
        return;
      }
      cb(path, buffer);
    });
  }

private:
  Socket socket_;
  boost::asio::io_context::strand strand_;
};