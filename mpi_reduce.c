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
     * 取得目前 Rank ID
     */
    MPI_Comm_rank(
        MPI_COMM_WORLD,
        &rank
    );


    /*
     * 取得 MPI process 數量
     */
    MPI_Comm_size(
        MPI_COMM_WORLD,
        &world_size
    );


    /*
     * 每個 Rank 建立自己的資料
     *
     * 例如：
     *
     * Rank0 -> 10
     * Rank1 -> 20
     * Rank2 -> 30
     * Rank3 -> 40
     *
     */
    int value = (rank + 1) * 10;


    int total = 0;


    /*
     * MPI_Reduce
     *
     * 將所有 Rank 的 value
     * 使用 SUM 加總
     *
     * root = 0
     *
     * 結果只會存在 Rank 0 的 total
     */
    MPI_Reduce(
        &value,
        &total,
        1,
        MPI_INT,
        MPI_SUM,
        0,
        MPI_COMM_WORLD
    );


    /*
     * 只有 Rank 0 可以看到結果
     */
    if (rank == 0)
    {
        printf(
            "Total sum = %d\n",
            total
        );
    }


    MPI_Finalize();

    return 0;
}
