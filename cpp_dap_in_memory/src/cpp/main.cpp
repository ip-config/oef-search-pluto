#include "cpp-sdk/src/cpp/DapServer.hpp"
#include "cpp_dap_in_memory/src/cpp/InMemoryDap.hpp"

#include <boost/program_options.hpp>

int main(int argc, char *argv[])
{
  try {
    std::string configfile, configjson;

    boost::program_options::options_description desc("Allowed options");
    desc.add_options()
      ("help", "produce help message")
      ("configjson", boost::program_options::value<std::string>(&configjson)->default_value(""), "Config string")
      ("configfile", boost::program_options::value<std::string>(&configfile)->default_value(""), "Config file name")
      ;

    boost::program_options::variables_map vm;
    boost::program_options::store(boost::program_options::parse_command_line(argc, argv, desc), vm);
    boost::program_options::notify(vm);

    if (vm.count("help"))
    {
      std::cout << desc << std::endl;
      exit(0);
    }

    DapServer<InMemoryDap> server;
    server.configure(configfile, configjson);
    server.run();
  }
  catch (std::exception & ex)
  {
    std::cerr << "ERROR:" << ex.what() << std::endl;
    exit(1);
  }
}
