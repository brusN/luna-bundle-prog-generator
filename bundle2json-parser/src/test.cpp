#include <mpi.h>

void c_init(int arg0, DF &arg1);
void c_iprint(int arg0);

int main(int argc, char **argv)
{
    int rank, size;
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    DF x;
    if (rank == 0)
    {
        c_init(7, x);
    }
    if (rank == 0)
    {
        c_print(x);
    }
    MPI_Finalize();
    return 0;
}
