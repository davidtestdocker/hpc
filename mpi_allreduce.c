// MPI C 範例：每個 rank 都執行同一份程式，依 rank 分支與 MPI 通訊交換資料。
// C 語法：& 取得變數位址供 MPI 寫入；* 宣告指標；分號結束敘述，大括號界定區塊。
#include <mpi.h>
#include <stdio.h>

int main(int argc, char** argv)
{
    /*
     * Initialize MPI environment.
     */
    // 初始化 MPI；argc／argv 的位址讓 MPI 處理啟動參數。
    MPI_Init(&argc, &argv);


    int rank;
    int world_size;


    /*
     * Get current process rank.
     */
    // 取得本程序在 communicator 中的編號，從 0 開始。
    MPI_Comm_rank(
        MPI_COMM_WORLD,
        &rank
    );


    /*
     * Get total number of MPI processes.
     */
    // 取得 communicator 中的程序總數。
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
    // 依序傳入送出位址、結果位址、元素數、型別、運算與群組；所有 rank 都取得總和。
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
    // 格式化輸出；%d 對應整數，\n 表示換行。
    printf(
        "Rank %d: local_value = %d, global_sum = %d\n",
        rank,
        local_value,
        global_sum
    );


    /*
     * Finalize MPI environment.
     */
    // 結束 MPI 環境並釋放相關資源。
    MPI_Finalize();


    return 0;
}
