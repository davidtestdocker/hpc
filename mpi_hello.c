#include <mpi.h>
#include <stdio.h>

int main(int argc, char** argv)
{
    /*
     * 初始化 MPI 環境
     *
     * 每一個 MPI process 啟動後，
     * 第一件事情就是加入 MPI runtime。
     *
     * 例如：
     * mpirun -np 4 ./mpi_hello
     *
     * 會建立 4 個 process，
     * 每個 process 都會執行這裡開始的程式。
     */
    MPI_Init(&argc, &argv);


    int world_size;
    int world_rank;


    /*
     * 取得 MPI communicator 裡總共有多少 process
     *
     * MPI_COMM_WORLD:
     * 代表目前所有 MPI process 的集合。
     *
     * 例如：
     * mpirun -np 4
     *
     * world_size = 4
     *
     * 代表目前有：
     * Rank 0
     * Rank 1
     * Rank 2
     * Rank 3
     */
    MPI_Comm_size(
        MPI_COMM_WORLD,
        &world_size
    );


    /*
     * 取得目前這個 process 的 Rank ID
     *
     * 每個 MPI process 都有自己的 rank。
     *
     * 例如：
     *
     * Process A -> Rank 0
     * Process B -> Rank 1
     * Process C -> Rank 2
     * Process D -> Rank 3
     *
     * Rank 是 MPI communication 的核心。
     * Process 之間靠 rank 找到彼此。
     */
    MPI_Comm_rank(
        MPI_COMM_WORLD,
        &world_rank
    );


    /*
     * 印出目前 process 的資訊
     *
     * 如果使用：
     *
     * mpirun -np 4 ./mpi_hello
     *
     * 會看到 4 個 process 各自輸出自己的 rank。
     */
    printf(
        "Hello from rank %d out of %d processes\n",
        world_rank,
        world_size
    );


    /*
     * 結束 MPI environment
     *
     * 所有 MPI communication 完成後，
     * 需要通知 MPI runtime 釋放資源。
     */
    MPI_Finalize();


    return 0;
}
