#include "parserlib.h"

/*
    ------------- RunSubblock impl -------------
*/

std::string& RunSubblock::getRank() {
    return rank;
}

void RunSubblock::setRank(std::string rank) {
    this->rank = rank;
}

std::list<std::string>& RunSubblock::getCfName() {
    return cfName;
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
                                            "\"rank\": " + "\"" + rank + "\"" + "," + 
                                            "\"cf\": " + buildNameForJSON() +
                                        "}";
    return buildString;
}

/*
    ------------- SendSubblock impl -------------
*/ 

std::string& SendSubblock::getFromRank() {
    return fromRank;
}

void SendSubblock::setFromRank(std::string fromRank) {
    this->fromRank = fromRank;
}

std::string& SendSubblock::getToRank() {
    return toRank;
}

void SendSubblock::setToRank(std::string toRank) {
    this->toRank = toRank;
}

DFDescriptor* SendSubblock::getDFD() {
    return dfd;
}

void SendSubblock::setDFD(DFDescriptor* dfd) {
    this->dfd = dfd;
}

std::string SendSubblock::toJSONStruct() {
    std::string buildString = std::string("{") + 
                                            "\"type\": \"send\"," + 
                                            "\"data\": " + dfd->to_cf_json_name() + "," +
                                            "\"from\": " + "\"" + fromRank + "\"" + "," +
                                            "\"to\": " + "\"" + toRank + "\"" + 
                                            "}";
    return buildString;
}

/*
    ------------- DefineDataFragmentBlock impl -------------
*/

std::string& DefineDataFragmentSubblock::getName() {
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

void ForSubblock::setBody(ExecutionContext* context) {
    body = context;
}

ExecutionContext* ForSubblock::getBody() {
    return body;
}

void ForSubblock::setIteratorName(std::string iteratorName) {
    this->iteratorName = iteratorName;
}

std::string& ForSubblock::getIteratorName() {
    return iteratorName;
}

void ForSubblock::setStartIndex(std::string startIndex) {
    this->startIndex = startIndex;
}

std::string ForSubblock::getStartIndex() {
    return startIndex;
}

void ForSubblock::setEndIndex(std::string endIndex) {
    this->endIndex = endIndex;
}

std::string ForSubblock::getEndIndex() {
    return endIndex;
}

std::string ForSubblock::toJSONStruct() {
    std::string buildString = std::string("{") + 
                                            "\"type\": \"for\"," + 
                                            "\"iterator\": \"" + iteratorName + "\"," + 
                                            "\"startValue\": \"" + startIndex + "\"," +
                                            "\"endValue\": \"" + endIndex + "\"," +
                                            "\"body\": " + body->toJSONStruct() + 
                                            "}";
    return buildString;
}

/*
    ------------- ExecutionContext impl -------------
*/

void ExecutionContext::addBlock(IExecuteSubblock* block) {
    body.emplace_back(block);
}

std::list<IExecuteSubblock*>& ExecutionContext::getBody() {
    return body;
}

std::string ExecutionContext::toJSONStruct() {
    std::string delimiter = ", ";
    std::string result = "[";
    auto it = body.begin();
    for (it; it != --body.end(); ++it) {
        result += (*it)->toJSONStruct() + delimiter;
    }
    result += (*it)->toJSONStruct() + "]";
    return result;
}

/*
    ------------- TaskDescriptor impl -------------
*/

std::list<std::string>& TaskDescriptor::getName() {
    return name;
}

void TaskDescriptor::setName(std::list<std::string> name) {
    this->name = name;
}

void TaskDescriptor::addNamePart(std::string namePart) {
    name.emplace_back(namePart);
}

/*
    ------------- DFDescriptor impl -------------
*/

std::list<std::string>& DFDescriptor::getName() {
    return name;
}

void DFDescriptor::setName(std::list<std::string> name) {
    this->name = name;
}

void DFDescriptor::addNamePart(std::string namePart) {
    name.emplace_back(namePart);
}

std::string DFDescriptor::to_cf_json_name() {
    auto dfNameIterator = name.begin();
    std::string dfName = "[\"" + *dfNameIterator + "\"";
    for (++dfNameIterator; dfNameIterator != name.end(); ++dfNameIterator) {
        dfName += ", \"" + *dfNameIterator + "\"";
    }
    dfName += "]";
    return dfName;
}

/*
    ------------- Bundle container impl -------------
*/

std::map<std::string, std::string>& BundleContainer::getMacroVars() {
    return macroVars;
}

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

std::string BundleContainer::registerNewDFD(DFDescriptor* dfd) 
{
    std::string dfdUUID = UUIDGenerator::generateUUID();
    dfs[dfdUUID] = dfd;
    return dfdUUID; 
}

DFDescriptor* BundleContainer::getDFDByUUID(std::string uuid) {
    return dfs[uuid];
}

std::string BundleContainer::registerNewContext(ExecutionContext* context) {
    std::string contextUUID = UUIDGenerator::generateUUID();
    contexts[contextUUID] = context;
    return contextUUID;
}

ExecutionContext* BundleContainer::getContextByUUID(std::string uuid) {
    return contexts[uuid];
}

void BundleContainer::setMainContext(ExecutionContext* context) {
    mainContext = context;
}

ExecutionContext* BundleContainer::getMainContext() {
    return mainContext;
}

BundleContainer::~BundleContainer() {
    // Execute blocks clear
    for (auto it = blocks.begin(); it != blocks.end(); ++it) {
        delete it->second;
    }

    // Task descriptors clear
    for (auto it = tasks.begin(); it != tasks.end(); ++it) {
        delete it->second;
    }

    // Execution contexts clear
    for (auto it = contexts.begin(); it != contexts.end(); ++it) {
        delete it->second;
    }

    for (auto it = dfs.begin(); it != dfs.end(); ++it) {
        delete it->second;
    }
}