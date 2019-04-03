#pragma once

#include <exception>

#include "proto.hpp"
#include "TransportFactory.hpp"

class DapException:public std::exception
{
public:
  DapException(int the_code, const std::string &the_msg) noexcept
    :code(the_code),
     msg(the_msg)
  {
  }
  ~DapException() = default;

  DapException(const DapException &other) noexcept
  {
    code = other.code;
    msg = other.msg;
  }

  DapException& operator=(const DapException &other) noexcept
  {
    code = other.code;
    msg = other.msg;
    return *this;
  }

  virtual const char* what() const noexcept
  {
    return msg.c_str();
  }
protected:
  int code;
  std::string msg;
};


class DapInterface {
public:
  DapInterface()
  {
  }

  virtual ~DapInterface() = default;

  virtual DapDescription describe() = 0;
  virtual Successfulness configure(const DapDescription&) = 0;
  virtual Successfulness update(const DapUpdate&) = 0;
  virtual Successfulness remove(const DapUpdate&) = 0;
  virtual ConstructQueryMementoResponse prepareConstraint(const ConstructQueryConstraintObjectRequest&) = 0;
  virtual ConstructQueryMementoResponse prepare(const ConstructQueryObjectRequest&) = 0;
  virtual IdentifierSequence execute(const DapExecute&) = 0;
};


class DapInterfaceTransportFactory : public TransportFactory, public std::enable_shared_from_this<DapInterfaceTransportFactory> {
public:
  DapInterfaceTransportFactory(std::shared_ptr<DapInterface> dap)
   : dap_(std::move(dap))
  {
  }

  virtual ~DapInterfaceTransportFactory() = default;

  virtual void SetReadCallbacks(std::shared_ptr<Transport> transport) {
    std::cout << "SET READ CALLBACKS" << std::endl;
    auto self(shared_from_this());
    std::cout << "SET READ CALLBACKS : self" << std::endl;

    transport->AddReadCallback<NoInputParameter>("describe",
        [self](NoInputParameter proto, Transport::TransportPtr tptr){
      tptr->write(self->dap_->describe());
    });

    transport->AddReadCallback<DapDescription>("configure",
        [self](DapDescription proto, Transport::TransportPtr tptr){
      tptr->write(self->dap_->configure(proto));
    });

    transport->AddReadCallback<DapUpdate>("update",
        [self](DapUpdate proto, Transport::TransportPtr tptr){
      tptr->write(self->dap_->update(proto));
    });
    transport->AddReadCallback<DapUpdate>("remove",
        [self](DapUpdate proto, Transport::TransportPtr tptr){
      tptr->write(self->dap_->remove(proto));
    });
    transport->AddReadCallback<ConstructQueryConstraintObjectRequest>("prepareConstraint",
        [self](ConstructQueryConstraintObjectRequest proto, Transport::TransportPtr tptr){
      tptr->write(self->dap_->prepareConstraint(proto));
    });
    transport->AddReadCallback<ConstructQueryObjectRequest>("prepare",
        [self](ConstructQueryObjectRequest proto, Transport::TransportPtr tptr){
      tptr->write(self->dap_->prepare(proto));
    });
    transport->AddReadCallback<DapExecute>("execute",
        [self](DapExecute proto, Transport::TransportPtr tptr){
      tptr->write(self->dap_->execute(proto));
    });
    std::cout << "SET READ CALLBACKS: end" << std::endl;
  }

private:
  std::shared_ptr<DapInterface> dap_;
};
