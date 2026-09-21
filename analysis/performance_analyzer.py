# 讀取已保存的 benchmark JSON，整理吞吐量與延遲，供不同併發設定比較。
# Python 語法：縮排界定區塊；def 定義函式，冒號後接區塊；型別註記說明預期型別。
import json
from pathlib import Path


RESULT_DIR = Path("benchmark/results")

FILES = {
    16: "vllm-c16-fixed.json",
    32: "vllm-c32-fixed.json",
    64: "vllm-c64.json",
}


# 定義 load_result 函式；參數由呼叫端傳入，return 將結果交還呼叫端。
def load_result(filename):
    path = RESULT_DIR / filename

    # with 在區塊結束時關閉檔案；json.load 從檔案讀取 JSON。
    with path.open() as file:
        return json.load(file)


# 定義 percent_change 函式；參數由呼叫端傳入，return 將結果交還呼叫端。
def percent_change(previous, current):
    # 百分比變化 = (新值 − 舊值) / 舊值 × 100；此公式假設舊值不為零。
    return ((current - previous) / previous) * 100


concurrencies = [16, 32, 64]

# [1:] 取第二個元素到尾端；zip 配成相鄰的 16→32 與 32→64 比較組。
for previous_concurrency, current_concurrency in zip(
    concurrencies,
    concurrencies[1:],
):
    previous_result = load_result(FILES[previous_concurrency])
    current_result = load_result(FILES[current_concurrency])

    throughput_change = percent_change(
        previous_result["request_throughput"],
        current_result["request_throughput"],
    )

    # TTFT 是首 token 延遲；TPOT 是每個輸出 token 時間，ITL 是 token 間隔延遲。
    ttft_change = percent_change(
        previous_result["mean_ttft_ms"],
        current_result["mean_ttft_ms"],
    )

    tpot_change = percent_change(
        previous_result["mean_tpot_ms"],
        current_result["mean_tpot_ms"],
    )

    itl_change = percent_change(
        previous_result["mean_itl_ms"],
        current_result["mean_itl_ms"],
    )

    print(
        f"\nConcurrency "
        f"{previous_concurrency} -> {current_concurrency}"
    )

    print(f"Throughput: {throughput_change:+.1f}%")
    print(f"Mean TTFT:  {ttft_change:+.1f}%")
    print(f"Mean TPOT:  {tpot_change:+.1f}%")
    print(f"Mean ITL:   {itl_change:+.1f}%")

    # 以延遲增幅與吞吐增幅比較，標示可能飽和；這是此組資料的啟發式判斷。
    if ttft_change > throughput_change:
        print("Diagnosis: SATURATION_CANDIDATE")
        print(
            "Reason: latency cost is growing faster "
            "than throughput gain"
        )
    else:
        print("Diagnosis: SCALING")
        print(
            "Reason: throughput gain still exceeds "
            "latency cost"
        )
