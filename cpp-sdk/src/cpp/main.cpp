#include <list>
#include <iostream>
#include <functional>

#include "Listener.hpp"
#include "cpp-sdk/src/cpp/DapInterface.hpp"

class TestDap : public DapInterface {
public:
  TestDap() = default;
  virtual ~TestDap() = default;

  virtual DapDescription describe() {
    DapDescription proto;
    return proto;
  }

  virtual Successfulness update(const DapUpdate&) {
    Successfulness proto;
    return proto;
  }

  virtual Successfulness remove(const DapUpdate&) {
    Successfulness proto;
    return proto;
  }

  virtual ConstructQueryMementoResponse prepareConstraint(const ConstructQueryConstraintObjectRequest&) {
    ConstructQueryMementoResponse proto;
    return proto;
  }

  virtual ConstructQueryMementoResponse prepare(const ConstructQueryObjectRequest&) {
    ConstructQueryMementoResponse proto;
    return proto;
  }

  virtual DapExecute execute(const IdentifierSequence&) {
    DapExecute proto;
    return proto;
  }
};


int main(int argc, char *argv[])
{
  std::cout << "Hello"<< std::endl;

  auto dap = std::make_shared<TestDap>();

  auto dap_factory = std::make_shared<DapInterfaceTransportFactory>(std::dynamic_pointer_cast<DapInterface>(dap));

  std::shared_ptr<Listener> listener = std::make_shared<Listener>(7600,
      std::dynamic_pointer_cast<TransportFactory>(dap_factory));

  listener->start_accept();
  listener->run();
}
