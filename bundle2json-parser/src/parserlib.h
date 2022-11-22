#include <iostream>
#include <list>
#include <map>
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

// Main container in bundle
class BundleContainer {
private:
    std::map<std::string, std::string> defines;
    std::list<IExecuteSubblock*> executeBlocks;

public:
    std::map<std::string, std::string> & getDefines();
    std::list<IExecuteSubblock*> & getExecuteBlocks();

    ~BundleContainer();
};