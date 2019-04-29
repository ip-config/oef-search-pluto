#!/bin/sh

set -e
set -x

bazel test dap_api/test/python:tests

bazel test dap_e_r_network/test/python:tests

bazel test dap_2d_geo/test/python:tests

bazel build dap_e_r_network/experimental/python:app &&   bazel-bin/dap_e_r_network/experimental/python/app

bazel build dap_2d_geo/experimental/python:app &&   bazel-bin/dap_2d_geo/experimental/python/app

bazel test dap_attribute_store/test/python:tests

bazel test ai_search_engine/test/python:tests

bazel test pluto_app/test/python:tests

set +x

echo ""
echo ""
echo ""
echo ""
echo "          \o/"
echo ""
echo ""
echo ""
echo ""
echo ""
