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