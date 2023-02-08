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
$(TARGET): $(OBJ_CPP) $(BUILD_DIR)lexer.o $(BIN_DIR)
	$(CC) $(OBJ_CPP) $(OBJ_C) -o $(TARGET)


## Compiling c++ files to object files
$(BUILD_DIR)%.o: $(PREF_SRC)%.cpp $(BUILD_DIR)
	$(CC) -c $< -o $@

$(BUILD_DIR)lexer.o: $(PREF_SRC)lexer.c $(BUILD_DIR)
	$(CC) -c $(PREF_SRC)lexer.c -o $(BUILD_DIR)lexer.o


# Compiling flex and bison files
$(PREF_SRC)lexer.c: 
	$(LEX_CC) -o $(PREF_SRC)lexer.c $(PREF_SRC)lexer.l

$(PREF_SRC)grammar.cpp:
	$(YACC_CC) -d --debug $(PREF_SRC)grammar.ypp -o $(PREF_SRC)grammar.cpp


# Creating bin and build dirs
$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(BIN_DIR):
	mkdir -p $(BIN_DIR)

clean:
	rm -rf $(BUILD_DIR) $(BIN_DIR) $(PREF_SRC)lexer.c $(PREF_SRC)grammar.cpp


if (rank == 0) {
	void * buff = new(val.get_ser_size());
	val.serialize(buff, val.get_ser_size());
	MPI_SEND();
}

if (rank == 1) {
	MPI
	void * buff = new(val.get_ser_size());
	MPI_Recv();
}

if (rank == 1)