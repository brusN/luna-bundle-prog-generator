#include <iostream>
#include "ucenv.h"

extern "C"
{
    void c_init_vector(DF& vectorDf, int size, int value) {
        vectorDf.create<int>(size);
        int* data = (int*)vectorDf.get_data();
        for (int i = 0; i < size; ++i) {
            data[i] = value;
        }
    }

    void c_get_vector_part(const DF& vectorDf, int partNumber, int partsCount, DF& vectorPartDf) {
        size_t vectorDfSize = vectorDf.get_size() / sizeof(int);
        int elementsPerPart = vectorDfSize / partsCount;
        int countPartsPlusOne = vectorDfSize % partsCount;

        // Getting start index for clone part from whole vector
        int startIndex = 0;
        for (int i = 1; i < partNumber; ++i) {
            startIndex += elementsPerPart;
            if (i <= countPartsPlusOne) {
                startIndex += 1;
            }
        }

        // Getting vector part size
        int vectorPartSize = elementsPerPart;
        if (partNumber <= countPartsPlusOne) {
            vectorPartSize += 1;
        }

        // Cloning vector part size
        vectorPartDf.create<int>(vectorPartSize);
        int* vectorData = (int *)vectorDf.get_data();
        int* vectorPartData = (int *)vectorPartDf.get_data();
        for (int i = 0, j = startIndex; i < vectorPartSize; ++i, ++j) {
            vectorPartData[i] = vectorData[j];
        }
    }

    void c_calc_scalar_mul(const DF& vector1, const DF& vector2, DF& result) {
        int* vector1Data = (int*)vector1.get_data();
        int* vector2Data = (int*)vector2.get_data();
        size_t size = vector1.get_size() / sizeof(int);
        int scalMulResult = 0;
        for (int i = 0; i < size; ++i) {
            scalMulResult += vector1Data[i] * vector2Data[i];
        }
        result.setValue(scalMulResult);
    }

    void c_init_df(DF& df, int value) {
        df.setValue(value);
    }

    void c_collect_result(const DF& resultPart, const DF& curResult, DF& nextCurResult) {
        nextCurResult.setValue(resultPart.get_int() + curResult.get_int());
    }

    void c_print_result(const DF& result) {
        printf("Scalar mul result: %d\n", result.get_int());
    }

    void c_print_info(const DF& vectorDf) {
        printf("%zu\n", vectorDf.get_size() / sizeof(int));
    }
}