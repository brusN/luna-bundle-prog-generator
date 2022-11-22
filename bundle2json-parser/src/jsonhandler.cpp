#include "jsonhandler.h"

std::string JSONHandler::buildValueString(std::string lvalue, std::string rvalue) {
    return "\"" + lvalue + "\": " + "\"" + rvalue + "\"";
}

void JSONHandler::generateJSON(std::ofstream &outputFile, BundleContainer &lunaBundle) {
    outputFile << "{";

    // Define block
    int curIndex = 0;
    int size = lunaBundle.getDefines().size();
    outputFile << "\"define\": {";
    for (auto define: lunaBundle.getDefines()) {
        curIndex += 1;
        auto jsonRecord = buildValueString(define.first, define.second);

        // For last element no need comma
        if (curIndex != size) {
            jsonRecord += ',';
        } else {
            jsonRecord += "},"; // Comma for execute blocks
        }

        outputFile << jsonRecord;
    }

    // Execute block
    curIndex = 0;
    size = lunaBundle.getExecuteBlocks().size();
    outputFile << "\"execute\": [";
    for (auto block: lunaBundle.getExecuteBlocks()) {
        curIndex += 1;
        auto jsonRecord = block->toJSONStruct();

        // For last element no need comma
        if (curIndex != size) {
            jsonRecord += ',';
        } else {
            jsonRecord += "]"; // No need comma for last block
        }
        
        outputFile << jsonRecord;
    }

    outputFile << "}";
}