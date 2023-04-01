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

class RunSubblock: public IExecuteSubblock {
private:
    std::string rank;
    std::list<std::string> cfName;

    std::string buildNameForJSON();

public:
    std::string getRank() const;
    void setRank(std::string rank);

    std::list<std::string> getCfName() const;
    void setCfName(std::list<std::string> task);

    std::string toJSONStruct();
};

class SendSubblock: public IExecuteSubblock {
private:
    std::string fromRank;
    std::string toRank;
    std::string dfName;

public:
    std::string getFromRank() const;
    void setFromRank(std::string fromRank);

    std::string getToRank() const;
    void setToRank(std::string toRank);

    std::string getDFName() const;
    void setDFName(std::string dfName);

    std::string toJSONStruct();
};

class DefineDataFragmentSubblock: public IExecuteSubblock {
private:
    std::string name;

public:
    std::string getName();
    void setName(std::string name);

    std::string toJSONStruct();
};

class ForSubblock: public IExecuteSubblock {
private:
    std::list<IExecuteSubblock *> body;
    std::string iteratorName;
    long startIndex;
    long endIndex;

public:
    void addBlockToBody(IExecuteSubblock* newBlock);
    void setIteratorName(std::string iteratorName);
    std::string getIteratorName();
    void setStartIndex(long startIndex);
    long getStartIndex();
    void setEndIndex(long endIndex);
    long getEndIndex();
};

class ExecutionContext {
private:
    std::list<IExecuteSubblock*> body;

public:
    void addBlock(IExecuteSubblock* block);
};

class TaskDescriptor {
private:
    std::list<std::string> name;

public:
    std::list<std::string> getName();
    void setName(std::list<std::string> name);
    void addNamePart(std::string namePart);
};

class UUIDGenerator {
public:
    static std::string generateUUID();
};

class BundleContainer {
private:
    std::map<std::string, std::string> macroVars;
    std::map<std::string, IExecuteSubblock*> blocks;
    std::map<std::string, TaskDescriptor*> tasks;
    std::map<std::string, 
    
public:
    void registerMacroVar(std::string varName, std::string value);
    std::string getMacroVarValueByName(std::string varName);

    std::string registerNewBlock(IExecuteSubblock* block);
    IExecuteSubblock* getBlockByUUID(std::string uuid);

    std::string registerNewTask(TaskDescriptor* task);
    TaskDescriptor* getTaskByUUID(std::string uuid);

    ~BundleContainer();
};