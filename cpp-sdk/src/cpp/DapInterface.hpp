#pragma once

#include "dap_api/src/protos/dap_description.pb.h"
#include "dap_api/src/protos/dap_interface.pb.h"
#include "dap_api/src/protos/dap_update.pb.h"
#include "cpp-sdk/src/cpp/TransportFactory.hpp"


class DapInterface {
public:
  DapInterface(const DapDescription& description)
   : description_{description}
  {
  }

  virtual ~DapInterface() = default;

  virtual const DapDescription& describe() {
    return description_;
  }

  virtual Successfulness update(const DapUpdate&) = 0;
  virtual Successfulness remove(const DapUpdate&) = 0;
  virtual ConstructQueryMementoResponse prepareConstraint(const ConstructQueryConstraintObjectRequest&) = 0;
  virtual ConstructQueryMementoResponse prepare(const ConstructQueryObjectRequest&) = 0;
  virtual DapExecute execute(const IdentifierSequence&) = 0;

protected:
  const DapDescription& description_;
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
    std::cout << "SET READ CALLBACKS: describe" << std::endl;

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
    transport->AddReadCallback<IdentifierSequence>("execute",
        [self](IdentifierSequence proto, Transport::TransportPtr tptr){
      tptr->write(self->dap_->execute(proto));
    });
    std::cout << "SET READ CALLBACKS: end" << std::endl;
  }

private:
  std::shared_ptr<DapInterface> dap_;
};