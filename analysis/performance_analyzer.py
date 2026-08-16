import json
from pathlib import Path


RESULT_DIR = Path("benchmark/results")

FILES = {
    16: "vllm-c16-fixed.json",
    32: "vllm-c32-fixed.json",
    64: "vllm-c64.json",
}


def load_result(filename):
    path = RESULT_DIR / filename

    with path.open() as file:
        return json.load(file)


def percent_change(previous, current):
    return ((current - previous) / previous) * 100


concurrencies = [16, 32, 64]

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
