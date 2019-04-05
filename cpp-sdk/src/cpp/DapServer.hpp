#pragma once

#include "Listener.hpp"
#include "DapInterface.hpp"
#include "DapException.hpp"

#include <iostream>
#include <fstream>


template <typename DapClass>
class DapServer {
public:
  using DapPtr                 = std::shared_ptr<DapClass>;
  using DapTransportFactoryPtr = std::shared_ptr<DapInterfaceTransportFactory>;
  using ServerPtr              = std::shared_ptr<Listener>;

  DapServer(const std::string &config_file="", const std::string &config_json="") {
    configure(config_file, config_json);
  }

  void configure(const std::string &config_file="", const std::string &config_json="")
  {
    if (config_file.length())
    {
      configureFromJsonFile(config_file);
    }
    if (config_json.length())
    {
      configureFromJson(config_json);
    }
  }

  void configureFromJsonFile(const std::string &config_file) {
    std::ifstream json_file(config_file);

    std::string json = "";
    if (!json_file.is_open()) {
      throw DapException(EIO, std::string("Failed to load: '") + config_file + "'");
    } else {
      std::string line;
      while (std::getline(json_file, line)) {
        json += line;
      }
    }

    try {
      configureFromJson(json);
    }
    catch (DapException &e)
    {
      throw DapException(EIO, std::string(e.what()) + " in '" + config_file + "'");
    }
  }

  void configureFromJson(const std::string &config_json) {

    auto status = google::protobuf::util::JsonStringToMessage(config_json, &dap_config_);
    if (!status.ok()) {
      throw DapException(EIO, std::string("Parse error: '") + status.ToString() + "'");
    }

    dap_ = std::make_shared<DapClass>();
    dap_ -> configure(dap_config_.description());
    dap_factory_ = std::make_shared<DapInterfaceTransportFactory>(std::dynamic_pointer_cast<DapInterface>(dap_));

    server_ = std::make_shared<Listener>(dap_config_.port(), std::dynamic_pointer_cast<TransportFactory>(dap_factory_));
  }

  void run() {

    if (!server_)
    {
      throw DapException(ENOTCONN, "No server started. Configuration failed?");
    }

    server_->start_accept();
    server_->run();
  }

private:
  DapConfig dap_config_;
  DapPtr dap_;
  DapTransportFactoryPtr dap_factory_;

  ServerPtr server_;
};
