#include <iostream>
#include <list>
#include <map>
#include <set>
#include <string>
#include <uuid/uuid.h>

// Inteface for subblock bodies
class IExecuteSubblock {
public:
    virtual std::string toJSONStruct() = 0;
};

class IIntExpression {
public:
    virtual std::string toJSONStruct() = 0;
    virtual ~IIntExpression();
};

class ExecutionContext: public IExecuteSubblock {
private:
    std::list<IExecuteSubblock*> body;

public:
    void addBlock(IExecuteSubblock* block);
    std::list<IExecuteSubblock*>& getBody();

    std::string toJSONStruct();
};

class TaskDescriptor {
private:
    std::string baseName;
    std::list<IIntExpression*> refs;

public:
    std::string& getBaseName();
    void setBaseName(std::string name);
    std::list<IIntExpression*>& getRefs();
    void addRef(IIntExpression* ref);
    std::string toJSONStruct();
};

class DFDescriptor {
private:
    std::string baseName;
    std::list<IIntExpression*> refs;

public:
    std::string& getBaseName();
    void setBaseName(std::string name);
    std::list<IIntExpression*>& getRefs();
    void addRef(IIntExpression* ref);
    std::string toJSONStruct();
};

class UUIDGenerator {
public:
    static std::string generateUUID() {
        uuid_t uuid;
        char uuidCharBuffer[37]; // 36 bytes uuid + '\0'
        uuid_generate(uuid);
        uuid_unparse(uuid, uuidCharBuffer);
        return std::string(uuidCharBuffer);
    }
};

class RunSubblock: public IExecuteSubblock {
private:
    TaskDescriptor* cf;
    IIntExpression* rank;
public:
    IIntExpression* getRank();
    void setRank(IIntExpression* rank);

    void setCf(TaskDescriptor* cf);
    TaskDescriptor* getCf();

    std::string toJSONStruct();
};

class SendSubblock: public IExecuteSubblock {
private:
    IIntExpression* fromRank;
    IIntExpression* toRank;
    DFDescriptor* dfd;

public:
    IIntExpression* getFromRank();
    void setFromRank(IIntExpression* fromRank);

    IIntExpression* getToRank();
    void setToRank(IIntExpression* toRank);

    DFDescriptor* getDFD();
    void setDFD(DFDescriptor* dfd);

    std::string toJSONStruct();
};

class DefineDataFragmentSubblock: public IExecuteSubblock {
private:
    std::string name;

public:
    std::string& getName();
    void setName(std::string name);

    std::string toJSONStruct();
};

class ForSubblock: public IExecuteSubblock {
private:
    ExecutionContext* body;
    std::string iteratorName;
    IIntExpression* startIndex;
    IIntExpression* endIndex;

public:
    void setBody(ExecutionContext* context);
    ExecutionContext* getBody();

    void setIteratorName(std::string iteratorName);
    std::string& getIteratorName();

    void setStartIndex(IIntExpression* startIndex);
    IIntExpression* getStartIndex();

    void setEndIndex(IIntExpression* endIndex);
    IIntExpression* getEndIndex();

    std::string toJSONStruct();
};

// Expressions

class ConstIntExpression: public IIntExpression {
private:
    int value;
public:
    ConstIntExpression(int value);
    void setValue(int value);
    int getValue();
    std::string toJSONStruct() override;
    ~ConstIntExpression() override;
};

class VarIntExpression: public IIntExpression {
private:
    std::string name;
public:
    VarIntExpression(std::string name);
    void setName(std::string name);
    std::string getName();
    std::string toJSONStruct() override;
    ~VarIntExpression() override;
};

class OperationIntExpression: public IIntExpression {
private:
    std::string op;
    IIntExpression* leftOperand;
    IIntExpression* rightOperand;

public:
    OperationIntExpression(std::string op, IIntExpression* leftOperand, IIntExpression* rightOperand);
    void setOperation(std::string op);
    std::string getOperation();
    void setLeftOperand(IIntExpression* operand);
    IIntExpression* getLeftOperand();
    void setRightOperand(IIntExpression* operand);
    IIntExpression* getRightOperand();
    std::string toJSONStruct();
    ~OperationIntExpression();
};

class BundleContainer {
private:
    std::map<std::string, std::string> macroVars;
    std::map<std::string, IExecuteSubblock*> blocks;
    std::map<std::string, TaskDescriptor*> tasks;
    std::map<std::string, ExecutionContext*> contexts;
    std::map<std::string, DFDescriptor*> dfs;
    std::map<std::string, IIntExpression*> expressions;

    // Memory will be cleared with other contexts
    ExecutionContext* mainContext;
    
public:
    std::map<std::string, std::string>& getMacroVars();
    void registerMacroVar(std::string varName, std::string value);
    std::string getMacroVarValueByName(std::string varName);

    std::string registerNewBlock(IExecuteSubblock* block);
    IExecuteSubblock* getBlockByUUID(std::string uuid);

    std::string registerNewTask(TaskDescriptor* task);
    TaskDescriptor* getTaskByUUID(std::string uuid);

    std::string registerNewContext(ExecutionContext* context);
    ExecutionContext* getContextByUUID(std::string uuid);

    void setMainContext(ExecutionContext* context);
    ExecutionContext* getMainContext();

    std::string registerNewDFD(DFDescriptor* dfd);
    DFDescriptor* getDFDByUUID(std::string uuid);

    std::string registerNewExpression(IIntExpression* expression);
    IIntExpression* getExpressionByUUID(std::string uuid);

    ~BundleContainer();
};