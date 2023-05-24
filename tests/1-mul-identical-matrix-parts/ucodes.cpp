#include <iostream>
#include "ucenv.h"

extern "C"
{
    void c_helloWorld()
    {
        printf("Hello world!\n");
    }

    void c_initMatrixPart(DF &matrixPart, int rows, int columns, int value)
    {
        matrixPart.create<int>(rows * columns);
        int *data = (int *)matrixPart.get_data();
        for (int i = 0; i < columns * rows; ++i)
        {
            data[i] = value;
        }
    }

    void c_multiplyMatrixParts(const DF &matrix1Part, int rows1, int columns1, const DF &matrix2Part, int rows2, int columns2, DF &matrixResult)
    {
        int *data1 = (int *)matrix1Part.get_data();
        int *data2 = (int *)matrix2Part.get_data();
        matrixResult.create<int>(rows1 * columns2);
        int *result = (int *)matrixResult.get_data();

        for (int i = 0; i < rows1; i++)
        {
            for (int j = 0; j < columns2; j++)
            {
                int sum = 0;
                for (int k = 0; k < columns1; k++)
                {
                    sum += data1[i * columns1 + k] * data2[k * columns2 + j];
                }
                result[i * columns2 + j] = sum;
            }
        }
    }

    void c_printMatrixPart(const DF &matrixPart, int rows, int columns)
    {
        int *data = (int *)matrixPart.get_data();
        for (int i = 0; i < rows; ++i)
        {
            for (int j = 0; j < columns; ++j)
            {
                printf("%d ", data[i * columns + j]);
            }
            printf("\n");
        }
    }
}
