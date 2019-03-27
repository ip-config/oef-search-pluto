#!/bin/sh

set -e
set -x

bazel test pluto_app/test/python:tests

bazel test dap_api/test/python:tests

bazel test dap_e_r_network/test/python:tests

bazel test dap_2d_geo/test/python:tests

bazel build dap_e_r_network/experimental/python:app &&   bazel-bin/dap_e_r_network/experimental/python/app

bazel build dap_2d_geo/experimental/python:app &&   bazel-bin/dap_2d_geo/experimental/python/app

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
