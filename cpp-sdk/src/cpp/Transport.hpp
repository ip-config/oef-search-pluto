#pragma once

#include "google/protobuf/message.h"
#include "cpp-sdk/src/cpp/ProtoFactory.hpp"
#include "cpp-sdk/src/cpp/CircularBuffer.hpp"
#include "cpp-sdk/src/cpp/char_array_buffer.hpp"
#include "cpp-sdk/src/cpp/Listener.hpp"


#include "boost/asio.hpp"
#include "boost/asio/ip/tcp.hpp"
#include "boost/asio/write.hpp"
#include "boost/asio/buffer.hpp"

#include <iostream>
#include <functional>
#include <unordered_map>


class Transport : Listener::ISocketOwner, public std::enable_shared_from_this<Transport> {
public:
  using Socket     = boost::asio::ip::tcp::socket;
  using SocketPtr  = std::shared_ptr<Socket>;
  using Buffer     = std::vector<uint8_t>;
  using BufferPtr  = std::shared_ptr<Buffer>;
  using Message    = google::protobuf::Message;
  using MessagePtr = std::shared_ptr<Message>;
  using ErrorCb    = std::function<void(std::error_code)>;
  using CbStore    = std::unordered_map<std::string, std::function<void(std::istream*)>>;
  using TransportPtr = std::shared_ptr<Transport>;

  Transport(Socket socket, ProtoFactory &protoFactory)
  : socket_(std::move(socket))
  , protoFactory_(protoFactory)
  , errorCb_{[](std::error_code){}}
  , read_buffer_(128) // 32KB
  {}
  virtual ~Transport() = default;

  virtual Socket& socket(){
    return socket_;
  }
  virtual void go(){
    read();
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

  void SetErrorCallback(ErrorCb errorCb){
    errorCb_ = errorCb;
  }

  template <class PROTO> void AddReadCallback(const std::string& path, std::function<void(PROTO, TransportPtr)> readCb){
    cb_store_[path] = [readCb, this](std::istream* is_ptr){
      PROTO proto;
      proto.ParseFromIstream(is_ptr);
      //TODO THREADPOOL DISPATCH here
      readCb(std::move(proto), shared_from_this());
    };
  }

  void read(const boost::system::error_code& ec = boost::system::error_code(), std::size_t length = 0){
    std::cerr << "Called read: " << ec << ", " << ec.message() << ", length = " << length << std::endl;

    if (ec != boost::system::errc::errc_t ::success){
      if (ec==boost::asio::error::eof){ //close connection
        std::cerr << "CONNECTION CLOSED" << std::endl;
      }
      //errorCb_(ec);
      return;
    }

    switch(state_){
      case States::START: {
        state_ = States::HEADER;
        stateData_.length = INT_SIZE;
        break;
      }

      case States::HEADER: {
        int32_t len = readHeader();
        if (len<0) {
          stateData_.length = static_cast<uint32_t>(-len);
          state_ = States::PATH;
        } else if (len>0) {
          stateData_.length = static_cast<uint32_t>(len);
          state_ = States::BODY;
        } else {
          std::cerr << "GOT CLOSE HEADER (length=0)!" << std::endl;
          return;
        }
        break;
      }

      case States::PATH: {
        setPath();
        state_ = States::BODY_HEADER;
        stateData_.length = INT_SIZE;
        break;
      }

      case States::BODY_HEADER: {
        int32_t len = readHeader();
        if (len<=0) {
          std::cerr << "WRONG BODY HEADER, PATH ALREADY RECEIVED (" << stateData_.path << ")!" << std::endl;
        } else {
          stateData_.length = static_cast<uint32_t>(len);
          state_ = States::BODY;
        }
        break;
      }

      case States::BODY: {
        gotBody();
        state_ = States::HEADER;
        stateData_.length = INT_SIZE;
        break;
      }
    }

    if (!active_.load()){
      return;
    }

    //issue read
    boost::asio::async_read(
        socket_,
        read_buffer_.getBuffersToWrite(stateData_.length),
        std::bind(&Transport::read, this, std::placeholders::_1, std::placeholders::_2)
    );

  }

  void stopRead(){
    active_.store(false);
  }

private:
  int32_t readHeader(){
    auto data = read_buffer_.getBuffersToRead();

    uint8_t *vec = nullptr;
    bool delete_needed = false;

    if (data.size()==1) {
      vec = static_cast<uint8_t*>(data[0].data());
    } else if (data.size()==2) {
      vec = new uint8_t[INT_SIZE];
      std::memcpy(vec, data[0].data(), data[0].size());
      std::memcpy(vec+data[0].size()-1, data[1].data(), data[1].size());
      delete_needed = true;
    } else {
      std::cerr << "readHeader error! Got data.size=" << data.size() << "!" <<std::endl;
      return 0;
    }

    auto len = static_cast<int32_t>(
        vec[3] << 24 |
        vec[2] << 16 |
        vec[1] << 8  |
        vec[0]
    );

    if (delete_needed) {
      delete vec;
    }

    return len;
  }

  void setPath() {
    auto data = read_buffer_.getBuffersToRead();
    char_array_buffer buffer(data);
    std::istream is(&buffer);
    std::string path((std::istream_iterator<char>(is)), std::istream_iterator<char>());

    std::cout << "-->PATH: " << path << std::endl;
    stateData_.path = path;
  }

  void gotBody() {
    std::cerr << std::endl << "GOT BODY " << std::endl;
    auto data = read_buffer_.getBuffersToRead();
    char_array_buffer buffer(data);
    buffer.diagnostic();
    std::istream is(&buffer);
    cb_store_[stateData_.path](&is);
  }

private:
  Socket socket_;
  ProtoFactory& protoFactory_;
  ErrorCb errorCb_;
  CircularBuffer read_buffer_;

  struct StateData {
    uint32_t length;
    std::string path;
  };

  enum States {
    START = 0,
    HEADER = 1,
    PATH = 2,
    BODY_HEADER = 3,
    BODY = 4
  };

  const uint32_t INT_SIZE = sizeof(int32_t);
  States state_ = {States::START};
  StateData stateData_ = {INT_SIZE, ""};
  std::atomic<bool> active_{true};

  CbStore cb_store_;
};