#include "dfmanager.h"

std::string DFDescriptor::getBaseName() {
    return baseName;
}

void DFDescriptor::setBaseName(std::string baseName) {
    this->baseName = baseName;
}

DF *DFDescriptor::getBaseValue() {
    return this->baseValue;
}

void DFDescriptor::setBaseValue(DF *value) {
    this->baseValue = value;
}

void DFDescriptor::addNewRef(std::list<std::string> refName) {
    this->refs.emplace(refName, new DF());
}

DF *DFDescriptor::getDFRefValue(std::list<std::string> refName) {
    return this->refs.find(refName)->second;
}

void DFDescriptor::setDFRefValue(std::list<std::string> refName, DF *value) {
    this->refs.find(refName)->second = value;
}

DFDescriptor::~DFDescriptor() {
    delete baseValue;
    for (auto ref: this->refs) {
        delete ref.second;
    }
}

DFDescriptor::DFDescriptor(std::string baseName) {
    this->baseName = baseName;
    this->baseValue = new DF();
}


void DFManager::addNewDF(DFDescriptor* dfDescriptor) {
    this->dfDescriptors.emplace(dfDescriptor->getBaseName(), dfDescriptor);
}

DFDescriptor* DFManager::getDFDescriptor(std::string dfName) {
    return this->dfDescriptors.find(dfName)->second;
}

DFManager::~DFManager() {
    for (auto df: this->dfDescriptors) {
        delete df.second;
    }
}

DF *DFManager::getDFByFullName(std::list<std::string> name) {
    auto dfd = this->dfDescriptors.find(name.front())->second;
    if (name.size() == 1) {
        return dfd->getBaseValue();
    } else {
        name.erase(name.begin());
        return dfd->getDFRefValue(name);
    }
}
