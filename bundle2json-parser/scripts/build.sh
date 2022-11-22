#!/bin/bash

# Script

clearBuildFolder () {
    rm -rf build/* 
    mkdir -p build
}

# Bison build
mkdir -p build

bison -d --debug src/grammar.ypp -o src/grammar.cpp
if [ $? != 0 ];
then
    echo '[Build] Bison build error!'
    clearBuildFolder
    exit 1
else
    echo '[Build] Bison build success!'
fi

# Flex build
flex -o src/lexer.c src/lexer.l 
if [ $? != 0 ]
then
    echo '[Build] Flex build error!'
    clearBuildFolder
    exit 1
else
    echo '[Build] Flex build success!'
fi

# Build parser

g++ src/parser.cpp src/parserlib.cpp src/grammar.cpp src/lexer.c src/jsonhandler.cpp -o bin/parser -std=c++14
echo '[Build] Build has finished successfully'
