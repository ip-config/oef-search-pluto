#pragma once

#include "asio_inc.hpp"
#include "CircularBuffer.hpp"
#include "char_array_buffer.hpp"
#include "network/src/proto/transport.pb.h"
#include "dap_api/src/protos/dap_update.pb.h"

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
  , write_buffer_(128) // 32KB
  , id_{id}
  {}

  virtual ~Transport() = default;

  virtual Socket& socket(){
    return socket_;
  }
  virtual void go(){
    read();
  }

  int get_id() { return id_; }

  template <typename PROTO> void write_message(const TransportHeader& header, const PROTO& body)
  {
    std::uint32_t header_byte_count = static_cast<uint32_t>(header.ByteSize());
    std::uint32_t body_byte_count   = static_cast<uint32_t>(body.ByteSize());
    std::uint32_t message_length_byte_count = sizeof(std::uint32_t);
    std::uint32_t total_space_needed = header_byte_count + body_byte_count + 2*message_length_byte_count;

    auto buffers = write_buffer_.getBuffersToWrite(total_space_needed);

    char_array_buffer serialised_message(buffers);

    serialised_message
        .write(header_byte_count)
        .write(body_byte_count);

    std::ostream os(&serialised_message);
    if (!header.SerializeToOstream(&os))
    {
      std::cerr << "Failed to write header proto." << std::endl;
    }

    if (!body.SerializeToOstream(&os))
    {
      std::cerr << "Failed to write body proto." << std::endl;
    }

    boost::asio::async_write(socket_, buffers, [total_space_needed](std::error_code ec,  std::size_t length){
      if (ec){
        std::cerr << "Failed to write to socket, because: " << ec.message() << "! "
                  << length <<" bytes written out of " << total_space_needed << std::endl;
      }
    });
  }

  template <typename PROTO> void write(const PROTO& proto, const std::string& path="") {
    TransportHeader header;
    header.set_uri(path);
    header.mutable_status()->set_success(true);
    std::string data;
    proto.SerializeToString(&data);

    write_message(header, proto);
  }

  void write_error(int32_t error_code, const std::vector<std::string>& narrative, const std::string& path="") {
    TransportHeader header;
    header.set_uri(path);
    auto* status = header.mutable_status();
    status->set_success(false);
    status->set_error_code(error_code);
    for(const auto& n : narrative) {
      status->add_narrative(n);
    }
    write_message(header, TransportHeader());
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
    if (ec)
    {
      std::cerr << "Called read: " << ec << ", " << ec.message() << ", length = " << length << std::endl;
    }

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
        stateData_.length = 2*INT_SIZE;
        break;
      }

      case States::HEADER: {
        if (readHeader()) {
          state_ = States::BODY;
        } else {
          std::cerr << "GOT CLOSE HEADER!" << std::endl;
          return;
        }
        break;
      }

      case States::BODY: {
        gotBody();
        state_ = States::HEADER;
        stateData_.length = 2*INT_SIZE;
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
  bool readHeader(){
    auto data = read_buffer_.getBuffersToRead();
    char_array_buffer buffer(data);
    buffer.read(stateData_.header_size).read(stateData_.body_size);

    stateData_.length = stateData_.header_size + stateData_.body_size;

    return stateData_.header_size > 0;
  }

  void gotBody() {
    auto data = read_buffer_.getBuffersToRead(stateData_.header_size);

    char_array_buffer hbuffer(data);
    std::istream h_is(&hbuffer);

    TransportHeader header;
    header.ParseFromIstream(&h_is);

    const std::string& path = header.uri();


    if (!header.status().success()) {
      std::cerr << "Network call got error as response (uri=" << path << "): error_code = "
                << header.status().error_code() << ", reason = " << std::endl;
      for(const auto& narrative : header.status().narrative()) {
        std::cerr<<"                                                          " << narrative << std::endl;
      }
      return;
    }

    auto cb_it = cb_store_.find(path);
    if (cb_it == cb_store_.end())
    {
      std::cerr << id_ << "Handler not registered for path: '" << path << "'" << std::endl;
      return;
    }

    auto bdata = read_buffer_.getBuffersToRead();

    char_array_buffer bbuffer(bdata);
    std::istream b_is(&bbuffer);

    cb_it->second(&b_is);
  }

private:
  Socket socket_;
  CircularBuffer read_buffer_;
  CircularBuffer write_buffer_;
  CbStore cb_store_;
  std::weak_ptr<IDestroyer> destroyer_;
  uint16_t id_;


  struct StateData {
    uint32_t length;
    uint32_t header_size;
    uint32_t body_size;
  };

  enum States {
    START = 0,
    HEADER = 1,
    BODY = 3
  };

  static constexpr const uint32_t INT_SIZE = sizeof(uint32_t);
  States state_ = {States::START};
  StateData stateData_ = {2*INT_SIZE, 0, 0};
  std::atomic<bool> active_{true};
};
