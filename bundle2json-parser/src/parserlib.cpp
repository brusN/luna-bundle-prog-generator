#include "parserlib.h"

std::string RunSubblock::getRank() const {
    return rank;
}

void RunSubblock::setRank(std::string rank) {
    this->rank = rank;
}

std::list<std::string> RunSubblock::getCfName() const {
    return this->cfName;
}

void RunSubblock::setCfName(std::list<std::string> task) {
    this->cfName = task;
}

std::string RunSubblock::buildNameForJSON() {
    auto cfNameIterator = cfName.begin();
    std::string taskName = "[\"" + *cfNameIterator + "\"";
    for (++cfNameIterator; cfNameIterator != cfName.end(); ++cfNameIterator) {
        taskName += ", \"" + *cfNameIterator + "\"";
    }
    taskName += "]";
    return taskName;
}

std::string RunSubblock::toJSONStruct() {
    std::string buildString = std::string("{") + 
                                            "\"type\": \"run\"," + 
                                            "\"rank\": " + rank + "," + 
                                            "\"cf\": \"" + buildNameForJSON() + "\"" +
                                        "}";
    return buildString;
}

std::string SendSubblock::getFromRank() const {
    return fromRank;
}

void SendSubblock::setFromRank(std::string fromRank) {
    this->fromRank = fromRank;
}

std::string SendSubblock::getToRank() const {
    return toRank;
}

void SendSubblock::setToRank(std::string toRank) {
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
                                            "\"from\": " + fromRank + "," +
                                            "\"to\": " + toRank + 
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

std::list<std::string> TaskDescriptor::getName() {
    return this->name;
}

void TaskDescriptor::setName(std::list<std::string> name) {
    this->name = name;
}

// Using Linux in-build libuuid 
std::string UUIDGenerator::generateUUID() {
    uuid_t uuid;
    char uuidCharBuffer[37]; // 36 bytes uuid + '\0'
    uuid_generate(uuid);
    uuid_unparse(uuid, uuidCharBuffer);
    return std::string(uuidCharBuffer);
}

BundleContainer::~BundleContainer() {
    for (auto it = blocks.begin(); it != blocks.end(); ++it) {
        delete it->second;
    }
}