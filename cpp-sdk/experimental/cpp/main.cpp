#include "cpp-sdk/experimental/cpp/EmbeddingDap.hpp"
#include "cpp-sdk/src/cpp/DapServer.hpp"


int main(int argc, char *argv[])
{
  DapServer<EmbeddingDap> server("cpp-sdk/experimental/resources/embedding_dap.json");
  server.run();
}
