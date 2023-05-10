#include <iostream>
#include <cstdio>
#include "jsonhandler.h"

extern "C" FILE *yyin;
int yyparse();

extern BundleContainer container;

int main(int argc, char *argv[]) {

    // Parsing from file
    FILE *input = std::fopen(argv[1], "r");
    if (!input) {
        fprintf(stderr, "Can't open the input file\n");
        return 1;
    }
    
    yyin = input;
    yyparse();
    std::fclose(input);

    std::ofstream jsonFile(argv[2]);
    JSONHandler JSONHandler;
    JSONHandler.generateJSON(jsonFile, container);
    jsonFile.close();
    return 0;
}