#include "parserlib.h"

/*
    ------------- RunSubblock impl -------------
*/

IIntExpression* RunSubblock::getRank() {
    return rank;
}

void RunSubblock::setRank(IIntExpression* rank) {
    this->rank = rank;
}

TaskDescriptor* RunSubblock::getCf() {
    return cf;
}

void RunSubblock::setCf(TaskDescriptor* cf) {
    this->cf = cf;
}

std::string RunSubblock::toJSONStruct() {
    std::string buildString = std::string("{") + 
                                            "\"type\": \"run\"," + 
                                            "\"rank\": " + rank->toJSONStruct() + "," +
                                            "\"cf\": " + cf->toJSONStruct() +
                                        "}";
    return buildString;
}

/*
    ------------- SendSubblock impl -------------
*/

IIntExpression* SendSubblock::getFromRank() {
    return fromRank;
}

void SendSubblock::setFromRank(IIntExpression*fromRank) {
    this->fromRank = fromRank;
}

IIntExpression* SendSubblock::getToRank() {
    return toRank;
}

void SendSubblock::setToRank(IIntExpression* toRank) {
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
                                "\"data\": " + dfd->toJSONStruct() + "," +
                                "\"from\": " + fromRank->toJSONStruct() + "," +
                                "\"to\": " + toRank->toJSONStruct() +
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
    std::string buildString = std::string("{"
                                            "\"type\": \"df\", "
                                            "\"name\": \"" + name + "\""
                                          "}");
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

void ForSubblock::setStartIndex(IIntExpression* startIndex) {
    this->startIndex = startIndex;
}

IIntExpression* ForSubblock::getStartIndex() {
    return startIndex;
}

void ForSubblock::setEndIndex(IIntExpression* endIndex) {
    this->endIndex = endIndex;
}

IIntExpression* ForSubblock::getEndIndex() {
    return endIndex;
}

std::string ForSubblock::toJSONStruct() {
    std::string buildString = std::string("{") + 
                                            "\"type\": \"for\"," + 
                                            "\"iterator\": \"" + iteratorName + "\"," + 
                                            "\"startValue\": " + startIndex->toJSONStruct() + "," +
                                            "\"endValue\": " + endIndex->toJSONStruct() + "," +
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

std::string& TaskDescriptor::getBaseName() {
    return baseName;
}

void TaskDescriptor::setBaseName(std::string name) {
    this->baseName = name;
}

std::list<IIntExpression*>& TaskDescriptor::getRefs() {
    return refs;
}

void TaskDescriptor::addRef(IIntExpression *ref) {
    refs.emplace_back(ref);
}

std::string TaskDescriptor::toJSONStruct() {
    std::string cfName = "[\"" + baseName + "\"";

    if (refs.size() == 0) {
        cfName += "]";
        return cfName;
    }

    for (auto ref: refs) {
        cfName += ", " + ref->toJSONStruct();
    }

    cfName += "]";
    return cfName;
}

/*
    ------------- DFDescriptor impl -------------
*/

std::string& DFDescriptor::getBaseName() {
    return baseName;
}

void DFDescriptor::setBaseName(std::string name) {
    this->baseName = name;
}

std::list<IIntExpression*>& DFDescriptor::getRefs() {
    return refs;
}

void DFDescriptor::addRef(IIntExpression *ref) {
    refs.emplace_back(ref);
}

std::string DFDescriptor::toJSONStruct() {
    std::string dfName = "[\"" + baseName + "\"";

    if (refs.size() == 0) {
        dfName += "]";
        return dfName;
    }

    for (auto ref: refs) {
        dfName += ", " + ref->toJSONStruct();
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

std::string BundleContainer::registerNewExpression(IIntExpression *expression) {
    std::string exprUUID = UUIDGenerator::generateUUID();
    expressions[exprUUID] = expression;
    return exprUUID;
}

IIntExpression* BundleContainer::getExpressionByUUID(std::string uuid) {
    return expressions[uuid];
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

ConstIntExpression::ConstIntExpression(int value) {
    this->value = value;
}

void ConstIntExpression::setValue(int value) {
    this->value = value;
}

int ConstIntExpression::getValue() {
    return value;
}

std::string ConstIntExpression::toJSONStruct() {
    std::string buildString = std::string("{") +
                              "\"type\": \"iconst\"," +
                              "\"value\": " + std::to_string(value) +
                              "}";
    return buildString;
}

ConstIntExpression::~ConstIntExpression() {
    // pass
}

VarIntExpression::VarIntExpression(std::string name) {
    this->name = name;
}

void VarIntExpression::setName(std::string name) {
    this->name = name;
}

std::string VarIntExpression::getName() {
    return name;
}

std::string VarIntExpression::toJSONStruct() {
    std::string buildString = std::string("{") +
                              "\"type\": \"var\"," +
                              "\"name\": \"" + name + "\""
                              "}";
    return buildString;
}

VarIntExpression::~VarIntExpression() {
    // pass
}

OperationIntExpression::OperationIntExpression(std::string op, IIntExpression *leftOperand, IIntExpression *rightOperand) {
    this->op = op;
    this->leftOperand = leftOperand;
    this->rightOperand = rightOperand;
}

void OperationIntExpression::setOperation(std::string op) {
    this->op = op;
}

std::string OperationIntExpression::getOperation() {
    return op;
}

void OperationIntExpression::setLeftOperand(IIntExpression *operand) {
    this->leftOperand = operand;
}

IIntExpression *OperationIntExpression::getLeftOperand() {
    return leftOperand;
}

void OperationIntExpression::setRightOperand(IIntExpression *operand) {
    this->rightOperand = operand;
}

IIntExpression *OperationIntExpression::getRightOperand() {
    return rightOperand;
}

std::string OperationIntExpression::toJSONStruct() {
    std::string buildString = std::string("{") +
                              "\"type\": \"" + op + "\"," +
                              "\"operands\": [" + leftOperand->toJSONStruct() + "," + rightOperand->toJSONStruct() + "]" +
                              "}";
    return buildString;
}

OperationIntExpression::~OperationIntExpression() {
    delete leftOperand;
    delete rightOperand;
}

IIntExpression::~IIntExpression() {

}
