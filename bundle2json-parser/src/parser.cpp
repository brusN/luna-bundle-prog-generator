#include <iostream>
#include <fstream>
#include <map>
#include <cstdio>
#include "jsonhandler.h"

extern "C" FILE *yyin;
int yyparse();

extern BundleContainer container;

int main(int argc, char *argv[]) {

    // Parsing from file

    FILE *input = std::fopen("files/input.bndl", "r");
    if (!input) {
        fprintf(stderr, "Can't open the input file\n");
        return 1;
    }
    
    yyin = input;
    yyparse();
    std::fclose(input);

    std::ofstream jsonFile("files/bundle.json");
    JSONHandler JSONHandler;
    JSONHandler.generateJSON(jsonFile, container);

    return 0;
}