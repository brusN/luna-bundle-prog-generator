flex -o src/lexer.c src/lexer.l
bison -d --debug src/grammar.ypp -o src/grammar.cpp
g++ -c src/lexer.c -o src/lexer.o