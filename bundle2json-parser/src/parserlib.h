#include <iostream>
#include <list>
#include <map>
#include <set>
#include <string>

// Inteface for subblock bodies
class IExecuteSubblock {
public:
    virtual std::string toJSONStruct() = 0;
};

class RunSubblock: public IExecuteSubblock {
private:
    int rank;
    std::string task;

public:

    int getRank() const;
    void setRank(int rank);

    std::string getTask() const;
    void setTask(std::string task);

    std::string toJSONStruct();
};

class SendSubblock: public IExecuteSubblock {
private:
    int fromRank;
    int toRank;
    std::string dfName;

public:
    int getFromRank() const;
    void setFromRank(int fromRank);

    int getToRank() const;
    void setToRank(int toRank);

    std::string getDFName() const;
    void setDFName(std::string dfName);

    std::string toJSONStruct();
};

enum DFType {
    DF_INT, DF_DOUBLE, DF_STRING, DF_NAME, DF_VALUE
};

class DefineDataFragmentBlock: public IExecuteSubblock {
private:
    std::string name;

public:
    std::string getName();
    void setName(std::string name);

    std::string toJSONStruct();
};

class BundleContainer {
private:
    std::map<std::string, std::string> defines;
    std::list<IExecuteSubblock*> executeBlocks;

public:
    std::map<std::string, std::string> & getDefines();
    std::list<IExecuteSubblock*> & getExecuteBlocks();

    ~BundleContainer();
};