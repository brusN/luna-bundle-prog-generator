TARGET_PARSER=./bin/luna-bundle-parser
TARGET_GENERATOR=./bin/luna-mpi-generator
CC=g++
PY_CC=pyinstaller
LEX_CC=flex
YACC_CC=bison

PREF_PY_SRC=./mpi-generator/src/
PREF_CPP_SRC=./bundle2json-parser/src/

BUILD_DIR=./build/
BIN_DIR=./bin/

SRC_CPP=$(wildcard $(PREF_CPP_SRC)*.cpp)
OBJ_CPP=$(patsubst $(PREF_CPP_SRC)%.cpp, $(BUILD_DIR)%.o, $(SRC_CPP))

all: $(TARGET_GENERATOR) $(TARGET_PARSER)
	rm -rf $(BUILD_DIR)

# Building generator module
$(TARGET_GENERATOR): $(TARGET_PARSER) $(PREF_PY_SRC)mpi_generator.py
	$(PY_CC) --onefile $(PREF_PY_SRC)mpi_generator.py --workpath $(BUILD_DIR) --specpath $(BUILD_DIR) --distpath $(BIN_DIR) -n luna-mpi-generator


# Building parser module
$(TARGET_PARSER): $(OBJ_CPP) $(BIN_DIR) $(BUILD_DIR)lexer.o $(BUILD_DIR)grammar.o
	$(CC) $(OBJ_CPP) $(BUILD_DIR)lexer.o $(BUILD_DIR)grammar.o -o $(TARGET_PARSER) -std=c++14


## Compiling c++ files to object files
$(BUILD_DIR)%.o: $(PREF_CPP_SRC)%.cpp $(BUILD_DIR)
	$(CC) -c $< -o $@


# Compiling flex and bison files
$(BUILD_DIR)lexer.o: $(PREF_CPP_SRC)lexer.c $(BUILD_DIR)
	$(CC) -c $(PREF_CPP_SRC)lexer.c -o $(BUILD_DIR)lexer.o

$(BUILD_DIR)grammar.o: $(PREF_CPP_SRC)grammar.cpp $(BUILD_DIR)
	$(CC) -c $(PREF_CPP_SRC)grammar.cpp -o $(BUILD_DIR)grammar.o

$(PREF_CPP_SRC)lexer.c: $(PREF_CPP_SRC)lexer.l $(PREF_CPP_SRC)grammar.cpp $(PREF_CPP_SRC)grammar.hpp
	$(LEX_CC) -o $(PREF_CPP_SRC)lexer.c $(PREF_CPP_SRC)lexer.l

$(PREF_CPP_SRC)grammar.cpp: $(PREF_CPP_SRC)grammar.ypp
	$(YACC_CC) -d --debug $(PREF_CPP_SRC)grammar.ypp -o $(PREF_CPP_SRC)grammar.cpp


# Creating bin and build dirs
$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(BIN_DIR):
	mkdir -p $(BIN_DIR)

clean:
	rm -rf $(BUILD_DIR) $(BIN_DIR) $(PREF_CPP_SRC)lexer.c $(PREF_CPP_SRC)grammar.cpp $(PREF_CPP_SRC)grammar.hpp