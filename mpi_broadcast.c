#include <mpi.h>
#include <stdio.h>

int main(int argc, char** argv)
{
    /*
     * 初始化 MPI environment
     */
    MPI_Init(&argc, &argv);


    int rank;
    int world_size;


    /*
     * 取得目前 process 的 rank
     */
    MPI_Comm_rank(
        MPI_COMM_WORLD,
        &rank
    );


    /*
     * 取得總共有多少 MPI process
     */
    MPI_Comm_size(
        MPI_COMM_WORLD,
        &world_size
    );


    int data;


    /*
     * 只有 Rank 0 建立資料
     *
     * 模擬：
     * Master process
     * 提供初始資料
     */
    if (rank == 0)
    {
        data = 100;

        printf(
            "Rank %d created data = %d\n",
            rank,
            data
        );
    }


    /*
     * MPI Broadcast
     *
     * root = 0
     *
     * 代表 Rank 0 是資料來源
     *
     * 執行後：
     * 所有 rank 都會拿到 data
     */
    MPI_Bcast(
        &data,
        1,
        MPI_INT,
        0,
        MPI_COMM_WORLD
    );


    /*
     * 每個 rank 印出收到的資料
     */
    printf(
        "Rank %d received data = %d\n",
        rank,
        data
    );


    /*
     * 結束 MPI
     */
    MPI_Finalize();


    return 0;
}
