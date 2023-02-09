TARGET=./bin/parser
CC=g++
LEX_CC=flex
YACC_CC=bison

PREF_SRC=./bundle2json-parser/src/
BUILD_DIR=./build/
BIN_DIR=./bin/

SRC_CPP=$(wildcard $(PREF_SRC)*.cpp)
OBJ_CPP=$(patsubst $(PREF_SRC)%.cpp, $(BUILD_DIR)%.o, $(SRC_CPP))


# Building parser module
$(TARGET): $(OBJ_CPP) $(BIN_DIR) $(BUILD_DIR)lexer.o $(BUILD_DIR)grammar.o
	$(CC) $(OBJ_CPP) $(BUILD_DIR)lexer.o $(BUILD_DIR)grammar.o -o $(TARGET) -std=c++14


## Compiling c++ files to object files
$(BUILD_DIR)%.o: $(PREF_SRC)%.cpp $(BUILD_DIR)
	$(CC) -c $< -o $@


# Compiling flex and bison files
$(BUILD_DIR)lexer.o: $(PREF_SRC)lexer.c
	$(CC) -c $(PREF_SRC)lexer.c -o $(BUILD_DIR)lexer.o

$(BUILD_DIR)grammar.o: $(PREF_SRC)grammar.cpp
	$(CC) -c $(PREF_SRC)grammar.cpp -o $(BUILD_DIR)grammar.o

$(PREF_SRC)lexer.c: $(PREF_SRC)lexer.l $(PREF_SRC)grammar.cpp $(PREF_SRC)grammar.hpp
	$(LEX_CC) -o $(PREF_SRC)lexer.c $(PREF_SRC)lexer.l

$(PREF_SRC)grammar.cpp: $(PREF_SRC)grammar.ypp
	$(YACC_CC) -d --debug $(PREF_SRC)grammar.ypp -o $(PREF_SRC)grammar.cpp


# Creating bin and build dirs
$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(BIN_DIR):
	mkdir -p $(BIN_DIR)

clean:
	rm -rf $(BUILD_DIR) $(BIN_DIR) $(PREF_SRC)lexer.c $(PREF_SRC)grammar.cpp $(PREF_SRC)grammar.hpp