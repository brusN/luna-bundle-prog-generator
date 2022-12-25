#include "parserlib.h"

int RunSubblock::getRank() const {
    return rank;
}

void RunSubblock::setRank(int rank) {
    this->rank = rank;
}

std::string RunSubblock::getTask() const {
    return task;
}

void RunSubblock::setTask(std::string task) {
    this->task = task;
}

std::string RunSubblock::toJSONStruct() {
    std::string buildString = std::string("{") + 
                                            "\"type\": \"run\"," + 
                                            "\"rank\": " + std::to_string(rank) + "," + 
                                            "\"cfs\": \"" + task + "\"" +
                                        "}";
    return buildString;
}

int SendSubblock::getFromRank() const {
    return fromRank;
}

void SendSubblock::setFromRank(int fromRank) {
    this->fromRank = fromRank;
}

int SendSubblock::getToRank() const {
    return toRank;
}

void SendSubblock::setToRank(int toRank) {
    this->toRank = toRank;
}

std::string SendSubblock::getDFName() const {
    return dfName;
}

void SendSubblock::setDFName(std::string dfName) {
    this->dfName = dfName;
}

std::string SendSubblock::toJSONStruct() {
    std::string buildString = std::string("{") + 
                                            "\"type\": \"send\"," + 
                                            "\"data\": \"" + dfName + "\"," + 
                                            "\"from\": " + std::to_string(fromRank) + "," +
                                            "\"to\": " + std::to_string(toRank) + 
                                            "}";
    return buildString;
}

std::string DefineDataFragmentBlock::getName() {
    return name;
}

void DefineDataFragmentBlock::setName(std::string name) {
    this->name = name;
}

std::string DefineDataFragmentBlock::toJSONStruct() {
    std::string buildString = std::string("{\"type\": \"df\", \"name\": \"" + name + "\"}");
    return buildString;
}

std::map<std::string, std::string>& BundleContainer::getDefines() {
    return defines;
}

std::list<IExecuteSubblock*>& BundleContainer::getExecuteBlocks() {
    return executeBlocks;
}

BundleContainer::~BundleContainer() {
    for (auto block: executeBlocks) {
        delete block;
    }
}