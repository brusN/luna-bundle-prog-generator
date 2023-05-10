#include "jsonhandler.h"

std::string JSONHandler::buildKeyValueString(std::string lvalue, std::string rvalue) {
    return "\"" + lvalue + "\": " + "\"" + rvalue + "\"";
}

void JSONHandler::generateJSON(std::ofstream &outputFile, BundleContainer &lunaBundle) {
    outputFile << "{";

    // Define block
    auto macroVars = lunaBundle.getMacroVars();
    outputFile << "\"define\": {";
    auto macroVarsIt = macroVars.begin();
    for (macroVarsIt; macroVarsIt != --macroVars.end(); ++macroVarsIt) {
        outputFile << buildKeyValueString(macroVarsIt->first, macroVarsIt->second) << ", ";
    }
    outputFile << buildKeyValueString(macroVarsIt->first, macroVarsIt->second) << "}, ";
    

    // Execute block
    auto mainExecutionContext = lunaBundle.getMainContext();
    outputFile << "\"execution\":";
    outputFile << mainExecutionContext->toJSONStruct();

    outputFile << "}";
}