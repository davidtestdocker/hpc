#include <mpi.h>
#include <stdio.h>

int main(int argc, char** argv)
{
    /*
     * Initialize MPI environment.
     */
    MPI_Init(&argc, &argv);


    int rank;


    /*
     * Get current process rank.
     */
    MPI_Comm_rank(
        MPI_COMM_WORLD,
        &rank
    );


    int data;


    /*
     * Rank 0 sends data to Rank 1.
     */
    if (rank == 0)
    {
        data = 123;

        /*
         * MPI_Send parameters:
         *
         * &data          -> send buffer
         * 1              -> number of elements
         * MPI_INT        -> data type
         * 1              -> destination rank
         * 0              -> message tag
         * MPI_COMM_WORLD -> communicator
         */
        MPI_Send(
            &data,
            1,
            MPI_INT,
            1,
            0,
            MPI_COMM_WORLD
        );

        printf(
            "Rank 0 sent data = %d to Rank 1\n",
            data
        );
    }


    /*
     * Rank 1 receives data from Rank 0.
     */
    else if (rank == 1)
    {
        /*
         * MPI_Recv parameters:
         *
         * &data          -> receive buffer
         * 1              -> number of elements
         * MPI_INT        -> data type
         * 0              -> source rank
         * 0              -> message tag
         * MPI_COMM_WORLD -> communicator
         * MPI_STATUS_IGNORE
         *                -> ignore extra receive status information
         */
        MPI_Recv(
            &data,
            1,
            MPI_INT,
            0,
            0,
            MPI_COMM_WORLD,
            MPI_STATUS_IGNORE
        );

        printf(
            "Rank 1 received data = %d from Rank 0\n",
            data
        );
    }


    /*
     * Finalize MPI environment.
     */
    MPI_Finalize();


    return 0;
}
