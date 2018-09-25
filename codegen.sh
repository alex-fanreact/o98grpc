#!/bin/bash
python -m grpc_tools.protoc --python_out=. --grpc_python_out=. other98.proto -I ./