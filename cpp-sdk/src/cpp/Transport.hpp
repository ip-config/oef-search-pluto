#pragma once

#include "asio_inc.hpp"
#include "CircularBuffer.hpp"
#include "char_array_buffer.hpp"


#include <iostream>
#include <functional>
#include <unordered_map>


class IDestroyer {
public:
  IDestroyer() = default;
  virtual ~IDestroyer() = default;

  virtual void destroy(uint16_t) = 0;
};


class ISocketOwner
{
public:
  ISocketOwner() {}
  virtual ~ISocketOwner() {}
  virtual boost::asio::ip::tcp::socket& socket() = 0;
  virtual void go() = 0;
};


class Transport : ISocketOwner, public std::enable_shared_from_this<Transport> {
public:
  using Socket       = boost::asio::ip::tcp::socket;
  using SocketPtr    = std::shared_ptr<Socket>;
  using Buffer       = std::vector<uint8_t>;
  using BufferPtr    = std::shared_ptr<Buffer>;
  using CbStore      = std::unordered_map<std::string, std::function<void(std::istream*)>>;
  using TransportPtr = std::shared_ptr<Transport>;

  Transport(Socket socket, uint16_t id)
  : socket_(std::move(socket))
  , read_buffer_(128) // 32KB
  , id_{id}
  {}

  virtual ~Transport() = default;

  virtual Socket& socket(){
    return socket_;
  }
  virtual void go(){
    read();
  }

  template <typename PROTO> void write(const PROTO& proto, const std::string& path="") {
    std::vector<boost::asio::const_buffer> buffers;
    auto path_size = static_cast<uint32_t>(path.size()+1);
    int32_t len = -static_cast<int32_t>(path_size);
    if (path.size()>1){
      buffers.emplace_back(boost::asio::buffer(&len, sizeof(len)));
      buffers.emplace_back(boost::asio::buffer(&path, path_size));
    }

    int data_size = proto.ByteSize();
    BufferPtr data = std::make_shared<Buffer>(data_size);
    proto.SerializeWithCachedSizesToArray(data->data());

    auto data_len = static_cast<uint32_t>(data_size);
    buffers.emplace_back(boost::asio::buffer(&data_len, sizeof(data_len)));
    buffers.emplace_back(boost::asio::buffer(data->data(), data_len));

    uint32_t total = static_cast<uint32_t>(-len+static_cast<int32_t>(sizeof(len)+data_len+sizeof(data_len)));
    boost::asio::async_write(socket_, buffers, [data, total](std::error_code ec,  std::size_t length){
      if (ec){
        std::cerr << "Failed to write to socket, because: " << ec.message() << "! "
                  << length <<" bytes written out of " << total << std::endl;
      }
    });
  }

  template <class PROTO> void AddReadCallback(const std::string& path, std::function<void(PROTO, TransportPtr)> readCb){
    cb_store_[path] = [readCb, this](std::istream* is_ptr){
      PROTO proto;
      proto.ParseFromIstream(is_ptr);
      //TODO THREADPOOL DISPATCH here
      readCb(proto, shared_from_this());
    };
  }

  void read(const boost::system::error_code& ec = boost::system::error_code(), std::size_t length = 0){
    //std::cerr << "Called read: " << ec << ", " << ec.message() << ", length = " << length << std::endl;

    if (ec){
      if (ec==boost::asio::error::eof){ //close connection
        std::cerr << "CONNECTION CLOSED" << std::endl;
        auto ptr = destroyer_.lock();
        if (ptr){
          ptr->destroy(id_);
        }
      }
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
        if (len<0) {
          std::cerr << "WRONG BODY HEADER (" << len << "), PATH ALREADY RECEIVED (" << stateData_.path << ")!" << std::endl;
        } else if (len==0) {
          gotBody();
          state_ = States::HEADER;
          stateData_.length = INT_SIZE;
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
    auto self(shared_from_this());
    boost::asio::async_read(socket_,read_buffer_.getBuffersToWrite(stateData_.length),
        [self](boost::system::error_code ec, std::size_t length){
      self->read(ec, length);
    });

  }

  void stopRead(){
    active_.store(false);
  }

  void close(){
    stopRead();
    socket_.close();
  }

  void SetDestroyer(std::weak_ptr<IDestroyer> destroyer){
    destroyer_ = destroyer;
  }

private:
  int32_t readHeader(){
    auto data = read_buffer_.getBuffersToRead();

    uint8_t *vec = nullptr;
    uint8_t extra_store[INT_SIZE];

    if (data.size()==1) {
      vec = static_cast<uint8_t*>(data[0].data());
    } else if (data.size()==2) {
      std::memcpy(extra_store, data[0].data(), sizeof(uint8_t)*data[0].size());
      std::memcpy(extra_store+data[0].size()-1, data[1].data(), sizeof(uint8_t)*data[1].size());
      vec = extra_store;
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

    return len;
  }

  void setPath() {
    auto data = read_buffer_.getBuffersToRead();
    char_array_buffer buffer(data);
    std::istream is(&buffer);
    std::string path((std::istream_iterator<char>(is)), std::istream_iterator<char>());

    //std::cout << "-->PATH: " << path << std::endl;
    stateData_.path = path;
  }

  void gotBody() {
    //std::cerr << std::endl << "GOT BODY " << std::endl;
    auto data = read_buffer_.getBuffersToRead();
    char_array_buffer buffer(data);

    std::istream is(&buffer);
    auto cb_it = cb_store_.find(stateData_.path);
    if (cb_it != cb_store_.end()){
      cb_it->second(&is);
    } else {
      std::cerr << "Handler not registered for path: " <<stateData_.path << std::endl;
    }
  }

private:
  Socket socket_;
  CircularBuffer read_buffer_;
  CbStore cb_store_;
  std::weak_ptr<IDestroyer> destroyer_;
  uint16_t id_;


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

  static constexpr const uint32_t INT_SIZE = sizeof(int32_t);
  States state_ = {States::START};
  StateData stateData_ = {INT_SIZE, ""};
  std::atomic<bool> active_{true};
};