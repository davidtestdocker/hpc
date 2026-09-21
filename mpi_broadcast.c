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
     * 取得目前 process 的 rank
     */
    // 取得本程序在 communicator 中的編號，從 0 開始。
    MPI_Comm_rank(
        MPI_COMM_WORLD,
        &rank
    );


    /*
     * 取得總共有多少 MPI process
     */
    // 取得 communicator 中的程序總數。
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

        // 格式化輸出；%d 對應整數，\n 表示換行。
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
    // 由指定 root 廣播資料；所有 rank 都必須參與呼叫。
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
    // 格式化輸出；%d 對應整數，\n 表示換行。
    printf(
        "Rank %d received data = %d\n",
        rank,
        data
    );


    /*
     * 結束 MPI
     */
    // 結束 MPI 環境並釋放相關資源。
    MPI_Finalize();


    return 0;
}
