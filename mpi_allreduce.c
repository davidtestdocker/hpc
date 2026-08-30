#include <mpi.h>
#include <stdio.h>

int main(int argc, char** argv)
{
    /*
     * Initialize MPI environment.
     */
    MPI_Init(&argc, &argv);


    int rank;
    int world_size;


    /*
     * Get current process rank.
     */
    MPI_Comm_rank(
        MPI_COMM_WORLD,
        &rank
    );


    /*
     * Get total number of MPI processes.
     */
    MPI_Comm_size(
        MPI_COMM_WORLD,
        &world_size
    );


    /*
     * Each rank creates its own local value.
     *
     * Rank 0 -> 10
     * Rank 1 -> 20
     * Rank 2 -> 30
     * Rank 3 -> 40
     */
    int local_value = (rank + 1) * 10;


    /*
     * This variable will store the final reduced result.
     *
     * Unlike MPI_Reduce, every rank will receive
     * the final result when using MPI_Allreduce.
     */
    int global_sum = 0;


    /*
     * MPI_Allreduce
     *
     * 1. Collect values from all ranks.
     * 2. Apply MPI_SUM.
     * 3. Send the final result back to every rank.
     *
     * Example:
     *
     * 10 + 20 + 30 + 40 = 100
     *
     * Final result:
     *
     * Rank 0 -> 100
     * Rank 1 -> 100
     * Rank 2 -> 100
     * Rank 3 -> 100
     */
    MPI_Allreduce(
        &local_value,
        &global_sum,
        1,
        MPI_INT,
        MPI_SUM,
        MPI_COMM_WORLD
    );


    /*
     * Print each rank's local value
     * and the global reduced result.
     */
    printf(
        "Rank %d: local_value = %d, global_sum = %d\n",
        rank,
        local_value,
        global_sum
    );


    /*
     * Finalize MPI environment.
     */
    MPI_Finalize();


    return 0;
}
