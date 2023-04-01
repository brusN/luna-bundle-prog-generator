#include "parserlib.h"

/*
    ------------- RubSubblock impl -------------
*/

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

/*
    ------------- SendSubblock impl -------------
*/ 

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

/*
    ------------- DefineDataFragmentBlock impl -------------
*/

std::string DefineDataFragmentSubblock::getName() {
    return name;
}

void DefineDataFragmentSubblock::setName(std::string name) {
    this->name = name;
}

std::string DefineDataFragmentSubblock::toJSONStruct() {
    std::string buildString = std::string("{\"type\": \"df\", \"name\": \"" + name + "\"}");
    return buildString;
}

/*
    ------------- ForSubblock impl -------------
*/

void ForSubblock::addBlockToBody(IExecuteSubblock* newBlock) {
    body.emplace_back(newBlock);
}

void ForSubblock::setIteratorName(std::string iteratorName) {
    this->iteratorName = iteratorName;
}

std::string ForSubblock::getIteratorName() {
    return iteratorName;
}

void ForSubblock::setStartIndex(long startIndex) {
    this->startIndex = startIndex;
}

long ForSubblock::getStartIndex() {
    return startIndex;
}

void ForSubblock::setEndIndex(long endIndex) {
    this->endIndex = endIndex;
}

long ForSubblock::getEndIndex() {
    return endIndex;
}

/*
    ------------- ExecutionContext impl -------------
*/

void ExecutionContext::addBlock(IExecuteSubblock* block) {
    body.emplace_back(block);
}

/*
    ------------- TaskDescriptor impl -------------
*/

std::list<std::string> TaskDescriptor::getName() {
    return this->name;
}

void TaskDescriptor::setName(std::list<std::string> name) {
    this->name = name;
}

void TaskDescriptor::addNamePart(std::string namePart) {
    name.emplace_back(namePart);
}

/*
   ------------- UUIDGenerator impl -------------
*/

// Using Linux in-build libuuid 
std::string UUIDGenerator::generateUUID() {
    uuid_t uuid;
    char uuidCharBuffer[37]; // 36 bytes uuid + '\0'
    uuid_generate(uuid);
    uuid_unparse(uuid, uuidCharBuffer);
    return std::string(uuidCharBuffer);
}

/*
    ------------- Bundle container impl -------------
*/

void BundleContainer::registerMacroVar(std::string varName, std::string value) {
    macroVars[varName] = value;
}

std::string BundleContainer::getMacroVarValueByName(std::string varName) {
    return macroVars[varName];
}

std::string BundleContainer::registerNewBlock(IExecuteSubblock* block) {
    std::string blockUUID = UUIDGenerator::generateUUID();
    blocks[blockUUID] = block;
    return blockUUID;
}

IExecuteSubblock* BundleContainer::getBlockByUUID(std::string uuid) {
    return blocks[uuid];
}

std::string BundleContainer::registerNewTask(TaskDescriptor* task) 
{
    std::string taskUUID = UUIDGenerator::generateUUID();
    tasks[taskUUID] = task;
    return taskUUID; 
}

TaskDescriptor* BundleContainer::getTaskByUUID(std::string uuid) {
    return tasks[uuid];
}

BundleContainer::~BundleContainer() {
    for (auto it = blocks.begin(); it != blocks.end(); ++it) {
        delete it->second;
    }
}