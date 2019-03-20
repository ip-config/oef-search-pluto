#pragma once

#include "cpp-sdk/src/cpp/Listener.hpp"
#include "cpp-sdk/src/cpp/DapInterface.hpp"

#include "cpp-sdk/experimental/protos/dap_config.pb.h"

#include "google/protobuf/util/json_util.h"

#include <iostream>
#include <fstream>


template <typename DapClass>
class DapServer {
public:
  using DapPtr                 = std::shared_ptr<DapClass>;
  using DapTransportFactoryPtr = std::shared_ptr<DapInterfaceTransportFactory>;
  using ServerPtr              = std::shared_ptr<Listener>;

  DapServer(const std::string config_file) {
    std::ifstream json_file(config_file);

    std::string json = "";
    if (!json_file.is_open()) {
      std::cerr << "Failed to load configuration file: " << config_file << std::endl;
      return;
    } else {
      std::string line;
      while (std::getline(json_file, line)) {
        json += line;
      }
    }

    auto status = google::protobuf::util::JsonStringToMessage(json, &dap_config_);
    if (!status.ok()) {
      std::cerr << "Config json parsing failed: " << status.ToString() << std::endl;
    }

    dap_ = std::make_shared<DapClass>();
    dap_factory_ = std::make_shared<DapInterfaceTransportFactory>(std::dynamic_pointer_cast<DapInterface>(dap_));

    server_ = std::make_shared<Listener>(dap_config_.port(), std::dynamic_pointer_cast<TransportFactory>(dap_factory_));
  }

  void run() {
    std::cout << "Starting " << dap_config_.description().name()
              << " dap on " << dap_config_.host() << ":" << dap_config_.port() << std::endl;

    server_->start_accept();
    server_->run();
  }

private:
  DapConfig dap_config_;
  DapPtr dap_;
  DapTransportFactoryPtr dap_factory_;

  ServerPtr server_;
};