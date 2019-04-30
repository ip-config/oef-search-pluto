#include "gtest/gtest.h"
#include <boost/asio.hpp>

#include "cpp-sdk/src/cpp/Transport.hpp"
#include "cpp-sdk/test/protos/testmessage.pb.h"
#include "cpp-sdk/src/cpp/char_array_buffer.hpp"

int success = 0;

class Core
{
public:
  using Context = boost::asio::io_context;
  using ContextPtr = std::shared_ptr<Context>;
  using Work = boost::asio::io_service::work;
  using WorkPtr = std::shared_ptr<Work>;

  ContextPtr context;
  volatile bool ending;
  WorkPtr work;

  operator Context*() { return context.get(); }
  operator Context&() { return *context; }

  Context *context_p() { return context.get(); }
  Context& context_r() { return *context; }

  Core()
  {
    ending = false;
    context = std::make_shared<Context>();
  }

  std::vector<std::thread> threads;

  void loop(void)
  {
     context -> run();
  }

  void run(int threadcount)
  {
    work = std::make_shared<Work>(*context);
    for(int i=0;i<threadcount;i++)
    {
      threads.push_back(std::thread{[this](){ loop(); }});
    }
  }

  virtual ~Core()
  {
    work.reset();
    context -> stop();
    for(auto &thr : threads)
    {
      thr.join();
    }
  }
};


class Endpoint
{
public:
  using Socket = boost::asio::ip::tcp::socket;
  using Resolver = boost::asio::ip::tcp::resolver;
  using Query = boost::asio::ip::tcp::resolver::query;
  using CorePtr = std::shared_ptr<Core>;
  using ResolverPtr = std::shared_ptr<Resolver>;
  using TransportPtr = std::shared_ptr<Transport>;

  CorePtr core;
  TransportPtr transport;
  ResolverPtr resolver;

  Endpoint(CorePtr thecore, int id):core(thecore)
  {
    Socket sock(core -> context_r() );
    transport = std::make_shared<Transport>(std::move(sock), id);
  }

  Socket &socket(void)
  {
    return transport -> socket();
  }


  // -- Server half ------------------------------------------a

  void incoming_connection(void)
  {
    transport -> AddReadCallback<TestMessage>("request", [this](const TestMessage &inbound_request_message, TransportPtr transport){
        handle_request(inbound_request_message);
      });

    transport -> read();
  }

  void handle_request(const TestMessage &inbound_request_message)
  {
    std::cout << "REQUESTED" << std::endl;
    TestMessage outbound_response_message;
    outbound_response_message.set_wibble(inbound_request_message.wibble() + "-ducks");
    transport -> write(outbound_response_message, "response");
    std::cout << "REQUEST HANDLED" << std::endl;
  }

  // -- Client half ------------------------------------------a

  void connect(int port)
  {
    resolver = std::make_shared<Resolver>(core -> context_r());
     Query q("127.0.0.1", std::to_string(port));

     std::cout << "RESOLVING" << std::endl;

     resolver -> async_resolve
       (
        q,
        [this](const boost::system::error_code &ec, boost::asio::ip::tcp::resolver::iterator it){ resolved(ec,it); }
        );
  }

  void resolved(const boost::system::error_code &ec,
                boost::asio::ip::tcp::resolver::iterator it)
  {
    std::cout << "RESOLVED"<<std::endl;
    if (ec)
    {
      exit(2);
    }
    transport -> socket() . async_connect
      (
       *it,
       [this](const boost::system::error_code &ec){ connected(ec); }
       );
  }

  void connected(const boost::system::error_code &ec)
  {
    std::cout << "CONNECTED"<<std::endl;
    transport -> AddReadCallback<TestMessage>("response", [this](const TestMessage &inbound_response_message, TransportPtr transport){
        handle_response(inbound_response_message);
      });

    TestMessage sender_request_message;
    sender_request_message.set_wibble("line-up");
    transport -> read();
    transport -> write(sender_request_message, "request");
  }

  void handle_response(const TestMessage &inbound_response_message)
  {
    std::cout << "RESPONSE" << std::endl;
    success = inbound_response_message.wibble() == "line-up-ducks";
    if (success)
    {
      std::cout << "SUCCESS" << std::endl;
    }
  }


};

class Listener
{
public:
  using Acceptor = boost::asio::ip::tcp::acceptor;
  using CorePtr = std::shared_ptr<Core>;
  using AcceptorPtr = std::shared_ptr<Acceptor>;
  using EndpointPtr = std::shared_ptr<Endpoint>;

  AcceptorPtr acceptor;
  CorePtr core;

  Listener(CorePtr thecore):core(thecore)
  {
  }

  void start_listen(int port)
  {
    acceptor = std::make_shared<Acceptor>(core -> context_r(), boost::asio::ip::tcp::endpoint(boost::asio::ip::tcp::v4(), port));
  }

  void start_accept()
  {
    EndpointPtr ep = std::make_shared<Endpoint>(core, 1);
    std::cout << "ACCEPTING!!"<<std::endl;
    acceptor -> async_accept(ep -> socket(),
                             [this, ep](const boost::system::error_code& error){
                               handle_accept(ep, error);
                             });
  }

  void handle_accept(EndpointPtr ep, const boost::system::error_code& error)
  {
    if (!error)
    {
      std::cout << "ACCEPTED" << std::endl;
      ep -> incoming_connection();
    }
    else
    {
      std::cout << "FAILED ACCEPT:" << error.message() << std::endl;
    }
  }

  ~Listener()
  {
  }
};


TEST(char_array_buffer_test, read_write_uint)
{
  std::vector<boost::asio::mutable_buffer> buffers;
  uint8_t buff[8];
  buffers.push_back(boost::asio::buffer(buff, 8));
  char_array_buffer buffer(buffers);

  uint32_t source = 53544;
  uint32_t target;
  buffer.write(source);

  char_array_buffer buffer_read(buffers);

  buffer_read.read(target);

  ASSERT_EQ(source, target);
}


TEST(message_test,content)
{
  using CorePtr = std::shared_ptr<Core>;

  CorePtr core = std::make_shared<Core>();
  core -> run(3);

  Listener listener(core);

  int port = 8000;
  while(port < 10000)
  {
    try
    {
      listener.start_listen(port);
      std::cout << "USING "<<port<<std::endl;
      break;
    }
    catch(...)
    {
      std::cout << "CANNOT BIND TO "<<port<<std::endl;
      port += 1;
      continue;
    }
  }

  if (port >= 10000)
  {
    exit(1);
  }
  listener.start_accept();

  sleep(1);

  Endpoint client(core, 2);
  std::cout << "CONNECT "<< port <<std::endl;
  client.connect(port);

  sleep(3);
  std::cout << "FINISH"<<std::endl;

  ASSERT_EQ(success, 1);
}
