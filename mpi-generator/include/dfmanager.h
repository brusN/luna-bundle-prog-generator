#ifndef LUNA_TEST_MANAGER_H
#define LUNA_TEST_MANAGER_H

#include <iostream>
#include <string>
#include <list>
#include <map>
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
public:
    void addNewDF(DFDescriptor* dfDescriptor);
    DFDescriptor* getDFDescriptor(std::string dfName);
    DF* getDFByFullName(std::list<std::string> name);

    ~DFManager();
};


#endif //LUNA_TEST_MANAGER_H
