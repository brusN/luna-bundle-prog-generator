#include <iostream>
#include <fstream>
#include <list>
#include "parserlib.h"


class IJSONHandler {
public:
    virtual void generateJSON(std::ofstream &outputFile, BundleContainer &lunaBundle) = 0;
};

class JSONHandler: public IJSONHandler {
private:
    std::string buildValueString(std::string lvalue, std::string rvalue);

public:
    void generateJSON(std::ofstream &outputFile, BundleContainer &lunaBundle);
};

