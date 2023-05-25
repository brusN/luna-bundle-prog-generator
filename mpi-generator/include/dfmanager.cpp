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
    if (this->refs.find(refName) == this->refs.end()) {
        this->refs[refName] = new DF();
    }
    return this->refs[refName];
}

void DFDescriptor::setDFRefValue(std::list<std::string> refName, DF *value) {
    this->refs.find(refName)->second = value;
}

DFDescriptor::~DFDescriptor() {
    delete baseValue;
    for (auto& ref: this->refs) {
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
    for (auto& df: this->dfDescriptors) {
        delete df.second;
    }
}

void DFManager::addRefToDF(std::string dfName, std::list<std::string> ref) {
    DFDescriptor* dfDescriptor = getDFDescriptor(dfName);
    dfDescriptor->addNewRef(ref);
}

DF *DFManager::getDFByFullName(std::list<std::string> name) {
    DFDescriptor* dfd = this->dfDescriptors.find(name.front())->second;
    DF* ptr;
    if (name.size() == 1) {
        ptr = dfd->getBaseValue();
    } else {
        name.erase(name.begin());
        ptr = dfd->getDFRefValue(name);
    }
    if (ptr == nullptr) {
        ptr = new DF();
    }
    return ptr;
}

void DFManager::sendDfBetweenNodes(std::list<std::string> dfName, int rank, int senderRank, int receiverRank) {
    int tag = ++tagCounter;
    if (rank == senderRank) {
        DF* df = getDFByFullName(dfName);
        size_t serializationSize = df->get_serialization_size();
        void* buff = malloc(serializationSize);
        df->serialize(buff, serializationSize);
        MPI_Send(buff, serializationSize, MPI_BYTE, receiverRank, tag, MPI_COMM_WORLD);
        free(buff);
    } else if (rank == receiverRank) {
        DF* df = getDFByFullName(dfName);
        MPI_Status status;
        MPI_Probe(senderRank, tag, MPI_COMM_WORLD, &status);
        int serializationSize;
        MPI_Get_count(&status, MPI_BYTE, &serializationSize);
        void* buff = malloc(serializationSize);
        MPI_Recv(buff, serializationSize, MPI_BYTE, senderRank, tag, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        df->deserialize(buff, serializationSize);
        free(buff);
    }
}
