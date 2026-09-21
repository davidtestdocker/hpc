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


    /*
     * Get current process rank.
     */
    // 取得本程序在 communicator 中的編號，從 0 開始。
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
        // 阻塞式送出：依序指定緩衝區、數量、型別、目的 rank、tag 與群組。
        MPI_Send(
            &data,
            1,
            MPI_INT,
            1,
            0,
            MPI_COMM_WORLD
        );

        // 格式化輸出；%d 對應整數，\n 表示換行。
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
        // 阻塞式接收：來源 rank 與 tag 必須匹配；MPI_STATUS_IGNORE 表示不保留狀態。
        MPI_Recv(
            &data,
            1,
            MPI_INT,
            0,
            0,
            MPI_COMM_WORLD,
            MPI_STATUS_IGNORE
        );

        // 格式化輸出；%d 對應整數，\n 表示換行。
        printf(
            "Rank 1 received data = %d from Rank 0\n",
            data
        );
    }


    /*
     * Finalize MPI environment.
     */
    // 結束 MPI 環境並釋放相關資源。
    MPI_Finalize();


    return 0;
}
