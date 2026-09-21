// MPI C 範例：每個 rank 都執行同一份程式，依 rank 分支與 MPI 通訊交換資料。
// C 語法：& 取得變數位址供 MPI 寫入；* 宣告指標；分號結束敘述，大括號界定區塊。
#include <mpi.h>
#include <stdio.h>

int main(int argc, char** argv)
{
    /*
     * 初始化 MPI environment
     */
    // 初始化 MPI；argc／argv 的位址讓 MPI 處理啟動參數。
    MPI_Init(&argc, &argv);


    int rank;
    int world_size;


    /*
     * 取得目前 Rank ID
     */
    // 取得本程序在 communicator 中的編號，從 0 開始。
    MPI_Comm_rank(
        MPI_COMM_WORLD,
        &rank
    );


    /*
     * 取得 MPI process 數量
     */
    // 取得 communicator 中的程序總數。
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
    // 歸約所有 rank 的值；只有指定 root 接收有效結果。
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
        // 格式化輸出；%d 對應整數，\n 表示換行。
        printf(
            "Total sum = %d\n",
            total
        );
    }


    // 結束 MPI 環境並釋放相關資源。
    MPI_Finalize();

    return 0;
}
