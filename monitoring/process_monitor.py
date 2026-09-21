# 執行 ps 取得程序 PID 與名稱，再輸出指令的標準輸出。
# Python 語法：縮排界定區塊；def 定義函式，冒號後接區塊；型別註記說明預期型別。
import subprocess

# 以參數清單執行外部程序；capture_output 收集輸出，text 解碼為字串。
result = subprocess.run(
    ["ps", "-eo", "pid,comm"],
    capture_output=True,
    text=True,
    check=False
)

print(result.stdout)
