#ifndef LUNA_TEST_MANAGER_H
#define LUNA_TEST_MANAGER_H

#include <iostream>
#include <mpi.h>
#include <string>
#include <list>
#include <map>
#include <atomic>
#include "df.h"

class DFDescriptor {
private:
    std::string baseName;
    DF* baseValue;
    std::map<std::list<std::string>, DF *> refs;
public:
    DFDescriptor(std::string baseName);

    std::string getBaseName();
    void setBaseName(std::string baseName);

    DF* getBaseValue();
    void setBaseValue(DF* value);

    void addNewRef(std::list<std::string> refName);
    DF* getDFRefValue(std::list<std::string> refName);
    void setDFRefValue(std::list<std::string> refName, DF* value);

    ~DFDescriptor();
};


class DFManager {
private:
    std::map<std::string, DFDescriptor *> dfDescriptors;
    std::atomic<int> tagCounter{0};
public:
    void addNewDF(DFDescriptor* dfDescriptor);
    DFDescriptor* getDFDescriptor(std::string dfName);
    void addRefToDF(std::string dfName, std::list<std::string> ref);
    DF* getDFByFullName(std::list<std::string> name);
    void sendDfBetweenNodes(std::list<std::string> dfName, int rank, int senderRank, int receiverRank);
    ~DFManager();
};


#endif //LUNA_TEST_MANAGER_H
