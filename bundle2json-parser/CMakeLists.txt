cmake_minimum_required(VERSION 3.26)
project(bundle2json_parser)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_FLAGS ${CMAKE_CXX_FLAGS} -luuid)

add_executable(bundle2json_parser src/parser.cpp src/parserlib.cpp src/jsonhandler.cpp src/lexer.o src/grammar.cpp)
