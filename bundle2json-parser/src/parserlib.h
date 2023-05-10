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
    std::list<std::string> name;

public:
    std::list<std::string>& getName();
    void setName(std::list<std::string> name);
    void addNamePart(std::string namePart);
};

class DFDescriptor {
private:
    std::list<std::string> name;

public:
    std::list<std::string>& getName();
    void setName(std::list<std::string> name);
    void addNamePart(std::string namePart);
    std::string to_cf_json_name();
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
    std::string rank;
    std::list<std::string> cfName;

    std::string buildNameForJSON();

public:
    std::string& getRank();
    void setRank(std::string rank);

    std::list<std::string>& getCfName();
    void setCfName(std::list<std::string> task);

    std::string toJSONStruct();
};

class SendSubblock: public IExecuteSubblock {
private:
    std::string fromRank;
    std::string toRank;
    DFDescriptor* dfd;

public:
    std::string& getFromRank();
    void setFromRank(std::string fromRank);

    std::string& getToRank();
    void setToRank(std::string toRank);

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
    std::string startIndex;
    std::string endIndex;

public:
    void setBody(ExecutionContext* context);
    ExecutionContext* getBody();

    void setIteratorName(std::string iteratorName);
    std::string& getIteratorName();

    void setStartIndex(std::string startIndex);
    std::string getStartIndex();

    void setEndIndex(std::string endIndex);
    std::string getEndIndex();

    std::string toJSONStruct();
};



class BundleContainer {
private:
    std::map<std::string, std::string> macroVars;
    std::map<std::string, IExecuteSubblock*> blocks;
    std::map<std::string, TaskDescriptor*> tasks;
    std::map<std::string, ExecutionContext*> contexts;
    std::map<std::string, DFDescriptor*> dfs;

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

    ~BundleContainer();
};